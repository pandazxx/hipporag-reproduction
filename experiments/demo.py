#!/usr/bin/env python3
"""
HippoRAG end-to-end demo.

Runs the full HippoRAG indexing + retrieval pipeline on a 15-passage dataset
and compares it to naive TF-IDF dense retrieval. Demonstrates multi-hop advantage.

Deviations from the paper (clearly labelled with [DEVIATION]):
  [DEVIATION-1] OpenIE: manually specified triples instead of GPT-3.5.
  [DEVIATION-2] Entity embeddings: character trigram hashing instead of Contriever.
  [DEVIATION-3] Query NER: character trigram matching instead of LLM extraction.
  [DEVIATION-4] ANN: brute-force numpy dot instead of FAISS IndexFlat.

Requirements: pip install numpy scipy
"""

import numpy as np
import scipy.sparse as sp
from collections import defaultdict


# =============================================================================
# DATASET: 15 passages about a fictional research lab
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
    "The Quantum Computing Lab received a $10M NSF grant in 2023.",                      # P14
]

# [DEVIATION-1] In the paper, GPT-3.5 extracts these triples via an OpenIE prompt.
# Here they are manually specified to keep the demo self-contained and free.
TRIPLES_PER_PASSAGE = {
    0:  [("Quantum Computing Lab", "founded by",   "Professor Alice Chen")],
    1:  [("Professor Alice Chen",  "published on", "quantum error correction")],
    2:  [("Quantum Computing Lab", "located at",   "Stanford University")],
    3:  [("Stanford University",   "is a",         "research university")],
    4:  [("Dr. Bob Martinez",      "works at",     "Quantum Computing Lab"),
         ("Dr. Bob Martinez",      "works on",     "quantum algorithms")],
    5:  [("Dr. Bob Martinez",      "supervised by","Professor Alice Chen")],
    6:  [("quantum algorithms",    "researched at","Stanford University")],
    7:  [("Professor Carol White", "director of",  "Physics department")],
    8:  [("Physics department",    "hosts",        "Quantum Computing Lab")],
    9:  [("Dr. Emily Davis",       "works at",     "Quantum Computing Lab"),
         ("Dr. Emily Davis",       "came from",    "Google Brain")],
    10: [("Google Brain",          "focused on",   "deep learning")],
    11: [("Dr. Emily Davis",       "works on",     "quantum machine learning")],
    12: [("Professor Alice Chen",  "received",     "Turing Award")],
    13: [("Turing Award",          "given by",     "Association for Computing Machinery")],
    14: [("Quantum Computing Lab", "received",     "NSF grant")],
}

TEST_QUESTIONS = [
    {
        "q":       "Who supervises the researcher working on quantum algorithms?",
        "answer":  "Professor Alice Chen",
        "hops":    2,
        "chain":   "quantum algorithms → Dr. Bob Martinez → Professor Alice Chen",
        "key_passages": {4, 5},   # P4: Bob works on QA; P5: Bob supervised by Alice
        # [DEVIATION-3] LLM would extract "quantum algorithms" as the NER entity.
        # We specify it directly to isolate the retrieval mechanism.
        "query_entities": ["quantum algorithms"],
    },
    {
        "q":       "What university hosts the lab that received the NSF grant?",
        "answer":  "Stanford University",
        "hops":    2,
        "chain":   "NSF grant → Quantum Computing Lab → Stanford University",
        "key_passages": {14, 2},  # P14: Lab got grant; P2: Lab at Stanford
        "query_entities": ["NSF grant"],
    },
    {
        "q":       "What award did the founder of the lab where Dr. Bob Martinez works receive?",
        "answer":  "Turing Award",
        "hops":    3,
        "chain":   "Dr. Bob Martinez → Quantum Computing Lab → Professor Alice Chen → Turing Award",
        "key_passages": {4, 0, 12},
        "query_entities": ["Dr. Bob Martinez"],
    },
    {
        "q":       "What research field does the organization Dr. Emily Davis came from focus on?",
        "answer":  "deep learning",
        "hops":    2,
        "chain":   "Dr. Emily Davis → Google Brain → deep learning",
        "key_passages": {9, 10},  # P9: Emily came from Google Brain; P10: GB = deep learning
        "query_entities": ["Dr. Emily Davis"],
    },
]


# =============================================================================
# ENTITY EMBEDDINGS (character trigram hashing)
# [DEVIATION-2] Paper uses facebook/contriever (768-dim dense embeddings).
# Here we use character trigrams hashed to 512 buckets — fast, no ML needed.
# Entities sharing substrings (e.g. "quantum algorithms" vs query containing
# that phrase) get higher cosine similarity.
# =============================================================================

EMBED_DIM = 512


def embed(text: str) -> np.ndarray:
    """Character trigram bag-of-hashes embedding, L2-normalised."""
    text = text.lower()
    vec = np.zeros(EMBED_DIM, dtype=np.float64)
    for i in range(max(1, len(text) - 2)):
        gram = text[i: i + 3]
        vec[abs(hash(gram)) % EMBED_DIM] += 1.0
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec


# =============================================================================
# INDEXING PHASE
# =============================================================================

def build_index(passages, triples_per_passage, sim_threshold=0.8):
    """
    Build the HippoRAG index from passages and triples.

    Returns a dict with:
      entities        list[str]   — all unique entities
      entity_idx      dict        — entity → integer index
      embeddings      ndarray     — (N, EMBED_DIM) L2-normalised entity vectors
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

    # --- Step 2: embed every entity ---
    embeddings = np.stack([embed(e) for e in entities])  # (N, EMBED_DIM)

    # --- Step 3: triple edges (E) ---
    # Each triple (s, p, o) adds a bidirectional edge between s and o.
    # Weight = co-occurrence count (number of triples linking the pair).
    graph: dict[tuple, float] = defaultdict(float)
    for _pidx, triples in triples_per_passage.items():
        for subj, _pred, obj in triples:
            si, oi = entity_idx[subj], entity_idx[obj]
            graph[(si, oi)] += 1.0
            graph[(oi, si)] += 1.0
    triple_edges = len(graph) // 2
    print(f"  Triple edges    : {triple_edges}")

    # --- Step 4: synonymy edges (E→) ---
    # [DEVIATION-4] Paper uses FAISS IndexFlat; we use brute-force numpy.
    # Paper uses Contriever cosine; we use trigram cosine (same formula, different vectors).
    # Threshold default = 0.8 (same as paper).
    sims = embeddings @ embeddings.T  # (N, N) pairwise cosine similarities
    syn_count = 0
    for i in range(N):
        for j in range(i + 1, N):
            if sims[i, j] >= sim_threshold:
                # Paper: assignment (=), not addition, when synonymy edge exists
                graph[(i, j)] = sims[i, j]
                graph[(j, i)] = sims[i, j]
                syn_count += 1
    print(f"  Synonymy edges  : {syn_count}  (cosine ≥ {sim_threshold})")
    print(f"  Total edges     : {triple_edges + syn_count}")

    # --- Step 5: build sparse adjacency matrix ---
    rows, cols, data = [], [], []
    for (i, j), w in graph.items():
        rows.append(i)
        cols.append(j)
        data.append(w)
    adj = sp.csr_matrix((data, (rows, cols)), shape=(N, N), dtype=np.float64)

    # --- Step 6: node specificity = 1 / |passages containing entity| ---
    specificity = np.array(
        [1.0 / len(entity_to_passages[e]) for e in entities], dtype=np.float64
    )

    # --- Step 7: P matrix (N × P) — entity appears in passage ---
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

    # Row-normalise adj → transition matrix T
    row_sums = np.array(adj.sum(axis=1), dtype=np.float64).flatten()
    row_sums[row_sums == 0] = 1.0
    T = sp.diags(1.0 / row_sums) @ adj   # T[i,j] = prob of walking from i → j

    # Personalisation vector s (uniform over seeds)
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
    Given a list of query entity strings (from LLM NER in the paper),
    run PPR and return (passage_idx, score) pairs sorted by score.
    """
    entities    = index["entities"]
    entity_idx  = index["entity_idx"]
    embeddings  = index["embeddings"]
    adj         = index["adj"]
    specificity = index["specificity"]
    P_matrix    = index["P_matrix"]

    # Match each query entity to KG nodes via embedding similarity
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

    # Personalized PageRank from seeds
    ppr = personalized_pagerank(adj, seed_indices)

    # Weight by node specificity
    weighted = ppr * specificity

    # Project onto passages: score[j] = sum_i weighted[i] * P[i,j]
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
    # Keep words that appear in fewer than 80% of passages (basic IDF filter)
    n = len(passages)
    filtered = [w for w in raw if raw[w] < 0.8 * n]
    vocab = {w: i for i, w in enumerate(filtered)}
    vecs = np.stack([_tfidf_vec(p, vocab, n, raw) for p in passages])
    return vocab, vecs


def _words(text: str) -> list[str]:
    import re
    return re.findall(r"[a-z]+", text.lower())


def _tfidf_vec(text: str, vocab: dict, n_docs: int, df: dict) -> np.ndarray:
    vec = np.zeros(len(vocab), dtype=np.float64)
    for w in _words(text):
        if w in vocab:
            tf = 1.0
            idf = np.log(n_docs / max(1, df[w]))
            vec[vocab[w]] += tf * idf
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
    sep = "=" * 68

    print(sep)
    print("HippoRAG End-to-End Demo")
    print(sep)
    print(f"\nCorpus: {len(PASSAGES)} passages  |  Questions: {len(TEST_QUESTIONS)}")
    print("\nDeviations from the paper:")
    print("  [DEVIATION-1] OpenIE triples are manually specified (not GPT-3.5).")
    print("  [DEVIATION-2] Embeddings: char trigrams (not Contriever).")
    print("  [DEVIATION-3] Query NER: query entities hard-coded (not LLM NER).")
    print("  [DEVIATION-4] ANN: brute-force numpy (not FAISS).")

    # ----- Phase 1: Indexing -----
    print(f"\n{sep}")
    print("Phase 1 — Indexing")
    print(sep)
    index = build_index(PASSAGES, TRIPLES_PER_PASSAGE, sim_threshold=0.8)

    vocab, passage_vecs = build_tfidf(PASSAGES)
    print(f"  TF-IDF vocab    : {len(vocab)} terms")

    # ----- Phase 2: Retrieval -----
    print(f"\n{sep}")
    print("Phase 2 — Retrieval")
    print(sep)

    hr_hit1 = 0   # at least 1 key passage in top-3
    bl_hit1 = 0
    hr_hit_all = 0  # ALL key passages in top-5
    bl_hit_all = 0

    for qi, q_data in enumerate(TEST_QUESTIONS):
        q      = q_data["q"]
        answer = q_data["answer"]
        hops   = q_data["hops"]
        chain  = q_data["chain"]
        key_p  = q_data["key_passages"]
        q_ents = q_data["query_entities"]

        print(f"\n{'─'*68}")
        print(f"Q{qi+1} ({hops}-hop): {q}")
        print(f"  Answer    : {answer}")
        print(f"  Hop chain : {chain}")
        print(f"  Key passages needed: {sorted(f'P{p}' for p in key_p)}")

        # HippoRAG
        print(f"\n  [HippoRAG]")
        hr = hipporag_retrieve(q_ents, index, top_k=5)
        print(f"    Top-5 passages (PPR × specificity):")
        for rank, (pidx, score) in enumerate(hr[:5]):
            mark = "✓" if pidx in key_p else " "
            print(f"      [{mark}] #{rank+1} P{pidx}  score={score:.5f}  "
                  f"\"{PASSAGES[pidx][:60]}...\"")

        hr_top3_set  = {pidx for pidx, _ in hr[:3]}
        hr_top5_set  = {pidx for pidx, _ in hr[:5]}
        hr_found1    = bool(key_p & hr_top3_set)
        hr_found_all = key_p.issubset(hr_top5_set)

        # Baseline
        print(f"\n  [Baseline — TF-IDF]")
        bl = tfidf_retrieve(q, vocab, passage_vecs, top_k=5)
        print(f"    Top-5 passages (cosine TF-IDF):")
        for rank, (pidx, score) in enumerate(bl[:5]):
            mark = "✓" if pidx in key_p else " "
            print(f"      [{mark}] #{rank+1} P{pidx}  sim={score:.3f}  "
                  f"\"{PASSAGES[pidx][:60]}...\"")

        bl_top3_set  = {pidx for pidx, _ in bl[:3]}
        bl_top5_set  = {pidx for pidx, _ in bl[:5]}
        bl_found1    = bool(key_p & bl_top3_set)
        bl_found_all = key_p.issubset(bl_top5_set)

        hr_hit1    += int(hr_found1)
        hr_hit_all += int(hr_found_all)
        bl_hit1    += int(bl_found1)
        bl_hit_all += int(bl_found_all)

        hr_icon = "✓" if hr_found1 else "✗"
        bl_icon = "✓" if bl_found1 else "✗"
        print(f"\n  ≥1 key passage in top-3:  HippoRAG {hr_icon}  |  Baseline {bl_icon}")

    # ----- Summary -----
    n = len(TEST_QUESTIONS)
    print(f"\n{sep}")
    print("Summary")
    print(sep)
    print(f"{'Metric':<42} {'HippoRAG':>10} {'Baseline':>10}")
    print(f"{'─'*42} {'─'*10} {'─'*10}")
    print(f"{'≥1 key passage in top-3':<42} {hr_hit1:>7}/{n:<3} {bl_hit1:>7}/{n}")
    print(f"{'All key passages in top-5':<42} {hr_hit_all:>7}/{n:<3} {bl_hit_all:>7}/{n}")
    print(sep)
    print()
    print("Note: HippoRAG advantage comes from PPR propagating through the KG.")
    print("      The baseline can only match passages whose text overlaps the query.")
    print("      Multi-hop questions require following entity chains across passages.")


if __name__ == "__main__":
    main()
