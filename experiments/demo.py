#!/usr/bin/env python3
"""
HippoRAG (v1) end-to-end demo.

Runs the full HippoRAG indexing + retrieval pipeline on the comparison dataset
(40 chronologically ordered memories about a single user; 22 multi-category
questions). Compares HippoRAG against a TF-IDF baseline; reports hit rates
broken down by question category and against each category's expected winner.

Deviations from the paper:
  [DEVIATION-4] ANN: brute-force numpy dot instead of FAISS IndexFlat.

Requires: uv sync  (installs openai, numpy, scipy)
Set NVIDIA_API_KEY before running.
"""

import re
from collections import defaultdict

import numpy as np
import scipy.sparse as sp

from _nim import (
    EMBED_MODEL, LLM_MODEL,
    embed, embed_batch,
    extract_triples, extract_query_entities,
)
from _dataset import (
    load_dataset, passages, memory_id_to_idx, required_indices,
    category_expected_winners, score_retrieval, aggregate_by_category,
    format_summary,
)

TOP_K_ANY = 5    # "any required fact retrieved in top-K_any?"
TOP_K_ALL = 10   # "all required facts retrieved in top-K_all?"


# =============================================================================
# INDEXING PHASE
# =============================================================================

def build_index(passages, triples_per_passage, sim_threshold=0.8):
    """
    Build the HippoRAG index from passages and triples.

    Returns a dict with:
      entities        list[str]   — all unique entities
      entity_idx      dict        — entity → integer index
      embeddings      ndarray     — (N, dim) L2-normalised entity vectors
      adj             csr_matrix  — (N, N) weighted adjacency (triple + synonymy edges)
      specificity     ndarray     — (N,) node specificity = 1 / |passages containing entity|
      P_matrix        csr_matrix  — (N, P) entity-to-passage presence matrix
    """
    P = len(passages)

    # --- Step 1: collect entities and entity→passage map ---
    entity_to_passages: dict[str, set] = defaultdict(set)
    for pidx, triples in triples_per_passage.items():
        for subj, _pred, obj in triples:
            entity_to_passages[subj].add(pidx)
            entity_to_passages[obj].add(pidx)

    entities = sorted(entity_to_passages.keys())
    entity_idx = {e: i for i, e in enumerate(entities)}
    N = len(entities)
    print(f"  Unique entities : {N}")

    # --- Step 2: embed every entity (one NIM API call for the whole batch) ---
    print(f"  Embedding {N} entities via NIM …")
    embeddings = embed_batch(entities)

    # --- Step 3: triple edges ---
    graph: dict[tuple, float] = defaultdict(float)
    for _pidx, triples in triples_per_passage.items():
        for subj, _pred, obj in triples:
            si, oi = entity_idx[subj], entity_idx[obj]
            graph[(si, oi)] += 1.0
            graph[(oi, si)] += 1.0
    triple_edges = len(graph) // 2
    print(f"  Triple edges    : {triple_edges}")

    # --- Step 4: synonymy edges ---
    # [DEVIATION-4] Paper uses FAISS IndexFlat; we use brute-force numpy.
    sims = embeddings @ embeddings.T
    syn_count = 0
    for i in range(N):
        for j in range(i + 1, N):
            if sims[i, j] >= sim_threshold:
                graph[(i, j)] = sims[i, j]
                graph[(j, i)] = sims[i, j]
                syn_count += 1
    print(f"  Synonymy edges  : {syn_count}  (cosine ≥ {sim_threshold})")
    print(f"  Total edges     : {triple_edges + syn_count}")

    # --- Step 5: sparse adjacency matrix ---
    rows, cols, data = [], [], []
    for (i, j), w in graph.items():
        rows.append(i)
        cols.append(j)
        data.append(w)
    adj = sp.csr_matrix((data, (rows, cols)), shape=(N, N), dtype=np.float64)

    # --- Step 6: node specificity ---
    specificity = np.array(
        [1.0 / len(entity_to_passages[e]) for e in entities], dtype=np.float64
    )

    # --- Step 7: P matrix (N × P) ---
    pr, pc = [], []
    for e, pidxs in entity_to_passages.items():
        ei = entity_idx[e]
        for pidx in pidxs:
            pr.append(ei)
            pc.append(pidx)
    P_matrix = sp.csr_matrix(
        (np.ones(len(pr), dtype=np.float64), (pr, pc)), shape=(N, P)
    )

    return dict(
        entities=entities,
        entity_idx=entity_idx,
        embeddings=embeddings,
        adj=adj,
        specificity=specificity,
        P_matrix=P_matrix,
    )


# =============================================================================
# PERSONALIZED PAGERANK (power iteration)
# =============================================================================

def personalized_pagerank(
    adj: sp.csr_matrix,
    seed_indices: list[int],
    alpha: float = 0.15,
    max_iter: int = 100,
    tol: float = 1e-8,
) -> np.ndarray:
    """
    Power iteration for Personalized PageRank.

    r_{t+1} = (1 - alpha) * T^T r_t + alpha * s
    where T is the row-stochastic transition matrix.
    alpha = 0.15 (paper uses 0.1; we keep 0.15 for slightly faster convergence).
    """
    N = adj.shape[0]

    row_sums = np.array(adj.sum(axis=1), dtype=np.float64).flatten()
    row_sums[row_sums == 0] = 1.0
    T = sp.diags(1.0 / row_sums) @ adj

    s = np.zeros(N, dtype=np.float64)
    if seed_indices:
        s[seed_indices] = 1.0 / len(seed_indices)

    r = s.copy()
    for _ in range(max_iter):
        r_new = (1.0 - alpha) * T.T.dot(r) + alpha * s
        if np.linalg.norm(r_new - r, 1) < tol:
            r = r_new
            break
        r = r_new
    return r


# =============================================================================
# HIPPORAG RETRIEVAL
# =============================================================================

def hipporag_retrieve(query_entities: list[str], index: dict, top_k: int = 5) -> list[tuple]:
    """
    Given query entity strings (extracted by NIM LLM), run PPR and return
    (passage_idx, score) pairs sorted by score.
    """
    entities    = index["entities"]
    embeddings  = index["embeddings"]
    adj         = index["adj"]
    specificity = index["specificity"]
    P_matrix    = index["P_matrix"]

    seed_indices: list[int] = []
    print(f"    Seed entities:")
    for qe in query_entities:
        qe_emb = embed(qe)
        sims = embeddings @ qe_emb
        best_idx = int(np.argmax(sims))
        best_sim = float(sims[best_idx])
        print(f"      '{qe}' → KG node '{entities[best_idx]}' (sim={best_sim:.3f})")
        if best_idx not in seed_indices:
            seed_indices.append(best_idx)

    ppr = personalized_pagerank(adj, seed_indices)
    weighted = ppr * specificity
    passage_scores = np.array(P_matrix.T.dot(weighted), dtype=np.float64).flatten()

    top_indices = np.argsort(-passage_scores)[:top_k]
    return [(int(i), float(passage_scores[i])) for i in top_indices if passage_scores[i] > 0]


# =============================================================================
# BASELINE: TF-IDF dense retrieval
# =============================================================================

def build_tfidf(passages: list[str]) -> tuple[dict, np.ndarray]:
    """Build a simple TF-IDF word-level representation over all passages."""
    raw = defaultdict(int)
    for p in passages:
        for w in _words(p):
            raw[w] += 1
    n = len(passages)
    filtered = [w for w in raw if raw[w] < 0.8 * n]
    vocab = {w: i for i, w in enumerate(filtered)}
    vecs = np.stack([_tfidf_vec(p, vocab, n, raw) for p in passages])
    return vocab, vecs


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z]+", text.lower())


def _tfidf_vec(text: str, vocab: dict, n_docs: int, df: dict) -> np.ndarray:
    vec = np.zeros(len(vocab), dtype=np.float64)
    for w in _words(text):
        if w in vocab:
            vec[vocab[w]] += np.log(n_docs / max(1, df[w]))
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec


def tfidf_retrieve(query: str, vocab: dict, passage_vecs: np.ndarray, top_k: int = 5) -> list[tuple]:
    q_vec = _tfidf_vec(query, vocab, len(passage_vecs), defaultdict(lambda: 1))
    sims = passage_vecs @ q_vec
    top = np.argsort(-sims)[:top_k]
    return [(int(i), float(sims[i])) for i in top if sims[i] > 0]


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
    print("HippoRAG v1 End-to-End Demo  (NIM-backed)")
    print(sep)
    print(f"\nDataset: {ds['metadata']['name']}  v{ds['metadata']['version']}")
    print(f"  {len(PASSAGES)} memories  |  {len(QUESTIONS)} questions  |  "
          f"{len(expected)} categories")
    print(f"LLM    : {LLM_MODEL}")
    print(f"Embed  : {EMBED_MODEL}")
    print(f"Top-K  : hit@{TOP_K_ANY}  |  all@{TOP_K_ALL}")
    print("\nRemaining deviation from the paper:")
    print("  [DEVIATION-4] ANN: brute-force numpy (not FAISS).")

    # ----- Phase 1a: OpenIE via NIM LLM -----
    print(f"\n{sep}")
    print("Phase 1a — OpenIE  (NIM LLM)")
    print(sep)
    triples_per_passage: dict[int, list[tuple]] = {}
    for i, passage in enumerate(PASSAGES):
        triples = extract_triples(passage)
        triples_per_passage[i] = triples
        mid = ds["memories"][i]["id"]
        print(f"  {mid} (P{i}): {len(triples)} triple(s)")

    # ----- Phase 1b: Build index -----
    print(f"\n{sep}")
    print("Phase 1b — Indexing")
    print(sep)
    index = build_index(PASSAGES, triples_per_passage, sim_threshold=0.8)

    vocab, passage_vecs = build_tfidf(PASSAGES)
    print(f"  TF-IDF vocab    : {len(vocab)} terms")

    # ----- Phase 2: Retrieval -----
    print(f"\n{sep}")
    print("Phase 2 — Retrieval")
    print(sep)

    hr_per_q: list[dict] = []
    bl_per_q: list[dict] = []

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

        # NIM NER
        q_ents = extract_query_entities(question)
        print(f"  NIM NER  : {q_ents}")

        # HippoRAG
        print(f"  [HippoRAG]")
        hr = hipporag_retrieve(q_ents, index, top_k=TOP_K_ALL)
        for rank, (pidx, score) in enumerate(hr[:TOP_K_ALL]):
            mark = "✓" if pidx in required else " "
            mid = ds["memories"][pidx]["id"]
            print(f"    [{mark}] #{rank+1:>2} {mid}  score={score:.5f}  "
                  f"\"{PASSAGES[pidx][:55]}...\"")

        hr_top_ids = [pidx for pidx, _ in hr]
        hr_any, hr_all = score_retrieval(hr_top_ids, required, TOP_K_ANY, TOP_K_ALL)
        hr_per_q.append({"category": cat, "found_any": hr_any, "found_all": hr_all})

        # Baseline
        print(f"  [Baseline — TF-IDF]")
        bl = tfidf_retrieve(question, vocab, passage_vecs, top_k=TOP_K_ALL)
        for rank, (pidx, score) in enumerate(bl[:TOP_K_ALL]):
            mark = "✓" if pidx in required else " "
            mid = ds["memories"][pidx]["id"]
            print(f"    [{mark}] #{rank+1:>2} {mid}  sim={score:.3f}    "
                  f"\"{PASSAGES[pidx][:55]}...\"")

        bl_top_ids = [pidx for pidx, _ in bl]
        bl_any, bl_all = score_retrieval(bl_top_ids, required, TOP_K_ANY, TOP_K_ALL)
        bl_per_q.append({"category": cat, "found_any": bl_any, "found_all": bl_all})

        def _icon(b):
            return "—" if b is None else ("✓" if b else "✗")
        print(f"  hit@{TOP_K_ANY}:  HippoRAG {_icon(hr_any)}  |  Baseline {_icon(bl_any)}    "
              f"all@{TOP_K_ALL}: HippoRAG {_icon(hr_all)}  |  Baseline {_icon(bl_all)}")

    # ----- Summary -----
    print(f"\n{sep}")
    print("Summary — HippoRAG")
    print(sep)
    print(format_summary(aggregate_by_category(hr_per_q), expected, TOP_K_ANY, TOP_K_ALL))
    print(f"\n{sep}")
    print("Summary — TF-IDF baseline")
    print(sep)
    print(format_summary(aggregate_by_category(bl_per_q), expected, TOP_K_ANY, TOP_K_ALL))
    print(sep)
    print()
    print("Note: absence_abstention questions have no requires_facts — they need a")
    print("      QA reader to score and are reported under 'Skip' above.")


if __name__ == "__main__":
    main()
