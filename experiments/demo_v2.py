#!/usr/bin/env python3
"""
HippoRAG 2 end-to-end demo (NIM-backed).

Same 15-passage corpus and 4 multi-hop questions as demo.py.

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


# =============================================================================
# DATASET (same as demo.py)
# =============================================================================

PASSAGES = [
    "The Quantum Computing Lab was founded by Professor Alice Chen in 2010.",             # P0
    "Professor Alice Chen has published over 200 papers on quantum error correction.",    # P1
    "The Quantum Computing Lab is located at Stanford University.",                       # P2
    "Stanford University is one of the top research universities in California.",         # P3
    "Dr. Bob Martinez works at the Quantum Computing Lab on quantum algorithms.",         # P4
    "Dr. Bob Martinez is supervised by Professor Alice Chen.",                            # P5
    "Quantum algorithms are a key research area at MIT and Stanford University.",         # P6
    "Professor Carol White is the director of the Physics department at Stanford University.",  # P7
    "The Physics department at Stanford University hosts the Quantum Computing Lab.",     # P8
    "Dr. Emily Davis recently joined the Quantum Computing Lab from Google Brain.",       # P9
    "Google Brain is a research division of Google focused on deep learning.",            # P10
    "Dr. Emily Davis works on quantum machine learning algorithms.",                      # P11
    "Professor Alice Chen received the Turing Award in 2019.",                            # P12
    "The Turing Award is given by the Association for Computing Machinery.",              # P13
    "The Quantum Computing Lab received a $10M NSF grant in 2023.",                       # P14
]

TEST_QUESTIONS = [
    {
        "q":            "Who supervises the researcher working on quantum algorithms?",
        "answer":       "Professor Alice Chen",
        "hops":         2,
        "chain":        "quantum algorithms → Dr. Bob Martinez → Professor Alice Chen",
        "key_passages": {4, 5},
    },
    {
        "q":            "What university hosts the lab that received the NSF grant?",
        "answer":       "Stanford University",
        "hops":         2,
        "chain":        "NSF grant → Quantum Computing Lab → Stanford University",
        "key_passages": {14, 2},
    },
    {
        "q":            "What award did the founder of the lab where Dr. Bob Martinez works receive?",
        "answer":       "Turing Award",
        "hops":         3,
        "chain":        "Dr. Bob Martinez → Quantum Computing Lab → Professor Alice Chen → Turing Award",
        "key_passages": {4, 0, 12},
    },
    {
        "q":            "What research field does the organization Dr. Emily Davis came from focus on?",
        "answer":       "deep learning",
        "hops":         2,
        "chain":        "Dr. Emily Davis → Google Brain → deep learning",
        "key_passages": {9, 10},
    },
]


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
) -> list[tuple[int, float]]:
    """HippoRAG 2 retrieval: query → top-K triples → LLM filter → PPR → passage scores."""
    # --- Step 1: query → triple matching ---
    q_emb = embed(query, input_type="query")

    if len(index["triples"]) > 0:
        triple_sims = index["triple_embs"] @ q_emb
        top_idx = np.argsort(-triple_sims)[:top_k_triples]
        top_triples     = [(index["triples"][i][0], index["triples"][i][1], index["triples"][i][2]) for i in top_idx]
        top_triple_sims = [float(triple_sims[i]) for i in top_idx]
    else:
        top_triples, top_triple_sims = [], []

    print(f"    Query→triple top-{len(top_triples)}:")
    for (s, p, o), sim in zip(top_triples, top_triple_sims):
        print(f"      ({sim:.3f}) ({s}, {p}, {o})")

    # --- Step 2: recognition memory (LLM filter) ---
    filtered = filter_triples(query, top_triples, top_k=4)
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
    return [(int(i), float(passage_scores[i])) for i in top_p if passage_scores[i] > 0]


# =============================================================================
# MAIN
# =============================================================================

def main():
    sep = "=" * 68

    print(sep)
    print("HippoRAG 2 End-to-End Demo  (NIM-backed)")
    print(sep)
    print(f"\nCorpus: {len(PASSAGES)} passages  |  Questions: {len(TEST_QUESTIONS)}")
    print(f"LLM    : {LLM_MODEL}")
    print(f"Embed  : {EMBED_MODEL}")

    print(f"\n{sep}")
    print("Phase 1 — OpenIE + Indexing")
    print(sep)
    index = build_index(PASSAGES, sim_threshold=0.75)

    print(f"\n{sep}")
    print("Phase 2 — Retrieval  (query→triple, recognition memory, PPR)")
    print(sep)

    hits1 = 0
    hits_all = 0

    for qi, q_data in enumerate(TEST_QUESTIONS):
        q       = q_data["q"]
        answer  = q_data["answer"]
        hops    = q_data["hops"]
        chain   = q_data["chain"]
        key_p   = q_data["key_passages"]

        print(f"\n{'─'*68}")
        print(f"Q{qi+1} ({hops}-hop): {q}")
        print(f"  Answer    : {answer}")
        print(f"  Hop chain : {chain}")
        print(f"  Key passages needed: {sorted(f'P{p}' for p in key_p)}")

        print(f"\n  [HippoRAG 2 retrieval]")
        hr = retrieve(q, index, top_k=5)
        print(f"    Top-5 passages (PPR on passage nodes):")
        for rank, (pidx, score) in enumerate(hr[:5]):
            mark = "✓" if pidx in key_p else " "
            print(f"      [{mark}] #{rank+1} P{pidx}  score={score:.5f}  "
                  f"\"{PASSAGES[pidx][:60]}...\"")

        top3 = {pidx for pidx, _ in hr[:3]}
        top5 = {pidx for pidx, _ in hr[:5]}
        found1   = bool(key_p & top3)
        found_all = key_p.issubset(top5)

        hits1    += int(found1)
        hits_all += int(found_all)

        icon = "✓" if found1 else "✗"
        print(f"\n  ≥1 key passage in top-3:  {icon}")

    n = len(TEST_QUESTIONS)
    print(f"\n{sep}")
    print("Summary")
    print(sep)
    print(f"{'Metric':<42} {'HippoRAG 2':>10}")
    print(f"{'─'*42} {'─'*10}")
    print(f"{'≥1 key passage in top-3':<42} {hits1:>7}/{n}")
    print(f"{'All key passages in top-5':<42} {hits_all:>7}/{n}")
    print(sep)
    print()
    print("Note: HippoRAG 2 retrieval differs from v1 in three ways:")
    print("  - Seeds come from query→triple matching + LLM filter (not query NER).")
    print("  - Passages are graph nodes seeded at low weight via query↔passage sim.")
    print("  - Final ranking reads PPR directly off passage nodes (no specificity).")


if __name__ == "__main__":
    main()
