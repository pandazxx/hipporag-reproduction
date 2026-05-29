#!/usr/bin/env python3
"""
HippoRAG 2 end-to-end demo (NIM-backed).

Same comparison dataset as demo.py (40 chronological memories, 22 questions
across 7 categories — single_hop, two_hop, deep_multi_hop, implicit_conceptual,
information_update, compositional_aggregation, absence_abstention).

What HippoRAG 2 changes vs HippoRAG 1:

  1. PASSAGE NODES IN THE GRAPH
     The graph contains both phrase nodes (extracted entities) AND passage
     nodes. Each phrase is connected to the passage(s) it appears in via
     "context edges". Passages are first-class graph citizens.

  2. QUERY → TRIPLE LINKING (instead of NER → phrase)
     v1 ran NER on the query and matched entity strings to phrase nodes.
     v2 embeds the whole query and retrieves the top-K most similar
     triples (using "subj pred obj" as the triple text).

  3. RECOGNITION MEMORY (online LLM filter)
     An LLM call filters the top-K retrieved triples down to the few that
     are actually relevant to the query. The kept triples' phrases become
     high-weight PPR seeds. All passages also seed PPR at low weight,
     scaled by query↔passage embedding similarity.

  4. RANKING
     PPR scores are read directly off the passage nodes — no node
     specificity weighting needed because passages are now graph nodes.

Requires: uv sync  (installs openai, numpy, scipy)
Set NVIDIA_API_KEY before running.
"""

from collections import defaultdict

import numpy as np
import scipy.sparse as sp

from _nim import (
    EMBED_MODEL, LLM_MODEL,
    embed, embed_batch,
    extract_triples, filter_triples,
)
from _dataset import (
    load_dataset, passages, memory_id_to_idx, required_indices,
    category_expected_winners, score_retrieval, aggregate_by_category,
    format_summary,
)
from _viz import render_index_overview, render_v2_trace, prepare_output_dir

TOP_K_ANY = 5
TOP_K_ALL = 10


# =============================================================================
# INDEXING
# =============================================================================

def build_index(passages: list[str], sim_threshold: float = 0.75) -> dict:
    """
    Build the HippoRAG 2 index from the corpus.

    Returns a dict with:
      phrases        list[str]   — unique entities extracted by OpenIE
      phrase_idx     dict        — phrase → graph node index (0 .. N_phrase-1)
      N_phrase, P, N int         — counts; passage node pidx lives at N_phrase + pidx
      phrase_embs    ndarray     — (N_phrase, dim) embeddings, "passage" input_type
      passage_embs   ndarray     — (P, dim) passage embeddings
      triples        list        — flat list of (subj, pred, obj, source_pidx)
      triple_embs    ndarray     — (T, dim) embeddings of "subj pred obj" strings
      adj            csr_matrix  — (N, N) symmetric weighted adjacency
    """
    # --- Step 1: OpenIE (NIM LLM) ---
    triples_per_passage: dict[int, list[tuple]] = {}
    for i, passage in enumerate(passages):
        triples_per_passage[i] = extract_triples(passage)
        print(f"  P{i}: {len(triples_per_passage[i])} triple(s)  {triples_per_passage[i]}")

    # --- Step 2: collect phrases + flat triple list ---
    phrase_set: set[str] = set()
    triples: list[tuple] = []  # (subj, pred, obj, pidx)
    for pidx, tps in triples_per_passage.items():
        for s, p, o in tps:
            phrase_set.add(s)
            phrase_set.add(o)
            triples.append((s, p, o, pidx))

    phrases = sorted(phrase_set)
    phrase_idx = {ph: i for i, ph in enumerate(phrases)}
    N_phrase = len(phrases)
    P = len(passages)
    N = N_phrase + P

    print(f"\n  Phrase nodes    : {N_phrase}")
    print(f"  Passage nodes   : {P}")
    print(f"  Total nodes     : {N}")
    print(f"  Total triples   : {len(triples)}")

    # --- Step 3: embed phrases, passages, and triple texts (one batch call each) ---
    print(f"\n  Embedding {N_phrase} phrases + {P} passages + {len(triples)} triple texts via NIM …")
    phrase_embs  = embed_batch(phrases)            if phrases else np.zeros((0, 1024))
    passage_embs = embed_batch(passages)           if passages else np.zeros((0, 1024))
    triple_texts = [f"{s} {p} {o}" for s, p, o, _ in triples]
    triple_embs  = embed_batch(triple_texts)       if triples  else np.zeros((0, phrase_embs.shape[1]))

    # --- Step 4: edges ---
    graph: dict[tuple[int, int], float] = defaultdict(float)

    # 4a. Relation edges (phrase ↔ phrase, from triples)
    relation_pairs: set[tuple[int, int]] = set()
    for s, _p, o, _pidx in triples:
        si, oi = phrase_idx[s], phrase_idx[o]
        if si == oi:
            continue
        graph[(si, oi)] = max(graph[(si, oi)], 1.0)
        graph[(oi, si)] = max(graph[(oi, si)], 1.0)
        relation_pairs.add(tuple(sorted([si, oi])))

    # 4b. Synonymy edges (phrase ↔ phrase, by embedding cosine ≥ threshold)
    syn_count = 0
    if N_phrase > 1:
        sims = phrase_embs @ phrase_embs.T
        for i in range(N_phrase):
            for j in range(i + 1, N_phrase):
                if sims[i, j] >= sim_threshold and tuple(sorted([i, j])) not in relation_pairs:
                    graph[(i, j)] = max(graph[(i, j)], float(sims[i, j]))
                    graph[(j, i)] = max(graph[(j, i)], float(sims[i, j]))
                    syn_count += 1

    # 4c. Context edges (phrase ↔ passage)
    context_count = 0
    seen_ctx: set[tuple[int, int]] = set()
    for s, _p, o, pidx in triples:
        pni = N_phrase + pidx
        for ei in (phrase_idx[s], phrase_idx[o]):
            key = (ei, pni)
            if key in seen_ctx:
                continue
            graph[(ei, pni)] = 1.0
            graph[(pni, ei)] = 1.0
            seen_ctx.add(key)
            context_count += 1

    print(f"  Relation edges  : {len(relation_pairs)}")
    print(f"  Synonymy edges  : {syn_count}  (cosine ≥ {sim_threshold})")
    print(f"  Context edges   : {context_count}")

    # --- Step 5: build sparse adjacency ---
    rows, cols, data = [], [], []
    for (i, j), w in graph.items():
        rows.append(i); cols.append(j); data.append(w)
    adj = sp.csr_matrix((data, (rows, cols)), shape=(N, N), dtype=np.float64)

    return dict(
        phrases=phrases, phrase_idx=phrase_idx,
        N_phrase=N_phrase, P=P, N=N,
        phrase_embs=phrase_embs, passage_embs=passage_embs,
        triples=triples, triple_embs=triple_embs,
        adj=adj,
    )


# =============================================================================
# PERSONALIZED PAGERANK
# =============================================================================

def personalized_pagerank(
    adj: sp.csr_matrix,
    seeds: np.ndarray,
    alpha: float = 0.15,
    max_iter: int = 100,
    tol: float = 1e-8,
) -> np.ndarray:
    """Power-iteration PPR with arbitrary (non-uniform) seed weights."""
    N = adj.shape[0]
    row_sums = np.array(adj.sum(axis=1), dtype=np.float64).flatten()
    row_sums[row_sums == 0] = 1.0
    T = sp.diags(1.0 / row_sums) @ adj

    if seeds.sum() > 0:
        s = seeds / seeds.sum()
    else:
        s = np.ones(N, dtype=np.float64) / N

    r = s.copy()
    for _ in range(max_iter):
        r_new = (1.0 - alpha) * T.T.dot(r) + alpha * s
        if np.linalg.norm(r_new - r, 1) < tol:
            r = r_new
            break
        r = r_new
    return r


# =============================================================================
# RETRIEVAL
# =============================================================================

def retrieve(
    query: str,
    index: dict,
    top_k_triples: int = 10,
    passage_seed_weight: float = 0.05,
    top_k: int = 5,
) -> dict:
    """HippoRAG 2 retrieval: query → top-K triples → LLM filter → PPR → passage scores.

    Returns a trace dict with intermediate state for visualisation.
    """
    # --- Step 1: query → triple matching ---
    q_emb = embed(query, input_type="query")

    if len(index["triples"]) > 0:
        triple_sims = index["triple_embs"] @ q_emb
        top_idx = np.argsort(-triple_sims)[:top_k_triples]
        top_triples = [(
            index["triples"][i][0],
            index["triples"][i][1],
            index["triples"][i][2],
            float(triple_sims[i]),
        ) for i in top_idx]
    else:
        top_triples = []

    print(f"    Query→triple top-{len(top_triples)}:")
    for s, p, o, sim in top_triples:
        print(f"      ({sim:.3f}) ({s}, {p}, {o})")

    # --- Step 2: recognition memory (LLM filter) ---
    filtered = filter_triples(query, [(s, p, o) for s, p, o, _ in top_triples], top_k=4)
    print(f"    Recognition memory kept {len(filtered)} triple(s):")
    for s, p, o in filtered:
        print(f"      ({s}, {p}, {o})")

    # --- Step 3: PPR seed vector ---
    seeds = np.zeros(index["N"], dtype=np.float64)

    # 3a. Phrase seeds from filtered triples (high weight)
    for s, _p, o in filtered:
        if s in index["phrase_idx"]:
            seeds[index["phrase_idx"][s]] += 1.0
        if o in index["phrase_idx"]:
            seeds[index["phrase_idx"][o]] += 1.0

    # 3b. Passage seeds scaled by query↔passage similarity (low weight)
    passage_sims = index["passage_embs"] @ q_emb  # (P,)
    for pidx in range(index["P"]):
        seeds[index["N_phrase"] + pidx] += passage_seed_weight * max(0.0, float(passage_sims[pidx]))

    if seeds.sum() == 0:
        for pidx in range(index["P"]):
            seeds[index["N_phrase"] + pidx] = 1.0 / index["P"]

    # --- Step 4: PPR ---
    ppr = personalized_pagerank(index["adj"], seeds)

    # --- Step 5: read passage scores ---
    passage_scores = ppr[index["N_phrase"]:]
    top_p = np.argsort(-passage_scores)[:top_k]
    top_passages = [(int(i), float(passage_scores[i])) for i in top_p if passage_scores[i] > 0]

    return {
        "top_triples": top_triples,
        "filtered_triples": filtered,
        "seeds": seeds,
        "ppr_scores": ppr,
        "top_passages": top_passages,
    }


# =============================================================================
# MAIN
# =============================================================================

def main():
    sep = "=" * 78

    ds = load_dataset()
    PASSAGES = passages(ds)
    QUESTIONS = ds["questions"]
    id_to_idx = memory_id_to_idx(ds)
    expected = category_expected_winners(ds)

    print(sep)
    print("HippoRAG 2 End-to-End Demo  (NIM-backed)")
    print(sep)
    print(f"\nDataset: {ds['metadata']['name']}  v{ds['metadata']['version']}")
    print(f"  {len(PASSAGES)} memories  |  {len(QUESTIONS)} questions  |  "
          f"{len(expected)} categories")
    print(f"LLM    : {LLM_MODEL}")
    print(f"Embed  : {EMBED_MODEL}")
    print(f"Top-K  : hit@{TOP_K_ANY}  |  all@{TOP_K_ALL}")

    print(f"\n{sep}")
    print("Phase 1 — OpenIE + Indexing")
    print(sep)
    index = build_index(PASSAGES, sim_threshold=0.75)

    # ----- Write index overview -----
    memory_ids = [m["id"] for m in ds["memories"]]
    out_dir = prepare_output_dir("v2")
    (out_dir / "index.md").write_text(
        render_index_overview(index, "HippoRAG 2", memory_ids, PASSAGES)
    )
    print(f"\n  Wrote index overview → {out_dir / 'index.md'}")

    print(f"\n{sep}")
    print("Phase 2 — Retrieval  (query→triple, recognition memory, PPR)")
    print(sep)

    per_q: list[dict] = []

    for qi, q in enumerate(QUESTIONS):
        question = q["question"]
        answer   = q["expected_answer"]
        cat      = q["category"]
        winner   = q["expected_winner"]
        required = required_indices(q, id_to_idx)
        req_ids  = q["requires_facts"]

        print(f"\n{'─'*78}")
        print(f"{q['id']} [{cat}, expect={winner}]: {question}")
        print(f"  Answer   : {answer}")
        print(f"  Required : {req_ids if req_ids else '(none — absence/abstention)'}")

        print(f"  [HippoRAG 2 retrieval]")
        trace = retrieve(question, index, top_k=TOP_K_ALL)
        for rank, (pidx, score) in enumerate(trace["top_passages"][:TOP_K_ALL]):
            mark = "✓" if pidx in required else " "
            mid = ds["memories"][pidx]["id"]
            print(f"    [{mark}] #{rank+1:>2} {mid}  score={score:.5f}  "
                  f"\"{PASSAGES[pidx][:55]}...\"")

        # Write per-question trace
        (out_dir / f"{q['id']}_trace.md").write_text(
            render_v2_trace(q, trace, index, memory_ids, PASSAGES, required)
        )

        top_ids = [pidx for pidx, _ in trace["top_passages"]]
        found_any, found_all = score_retrieval(top_ids, required, TOP_K_ANY, TOP_K_ALL)
        per_q.append({"category": cat, "found_any": found_any, "found_all": found_all})

        def _icon(b):
            return "—" if b is None else ("✓" if b else "✗")
        print(f"  hit@{TOP_K_ANY}: {_icon(found_any)}   all@{TOP_K_ALL}: {_icon(found_all)}")

    # ----- Summary -----
    print(f"\n{sep}")
    print("Summary — HippoRAG 2")
    print(sep)
    print(format_summary(aggregate_by_category(per_q), expected, TOP_K_ANY, TOP_K_ALL))
    print(sep)
    print()
    print("Note: absence_abstention questions have no requires_facts — they need a")
    print("      QA reader to score and are reported under 'Skip' above.")
    print("      HippoRAG 2 retrieval differs from v1 in three ways:")
    print("        - Seeds come from query→triple + LLM filter, not query NER.")
    print("        - Passages are graph nodes seeded by query↔passage similarity.")
    print("        - Final ranking reads PPR off passage nodes (no specificity).")
    print("  - Final ranking reads PPR directly off passage nodes (no specificity).")


if __name__ == "__main__":
    main()
