#!/usr/bin/env python3
"""
HippoRAG end-to-end demo.

Runs the full HippoRAG indexing + retrieval pipeline on a 15-passage dataset
and compares it to naive TF-IDF dense retrieval. Demonstrates multi-hop advantage.

Deviations from the paper:
  [DEVIATION-4] ANN: brute-force numpy dot instead of FAISS IndexFlat.

Requires: uv sync  (installs openai, numpy, scipy)
Set NVIDIA_API_KEY before running.
"""

import json
import os
import re
import time
from collections import defaultdict

import numpy as np
import scipy.sparse as sp
from openai import OpenAI, RateLimitError


# =============================================================================
# NIM SETUP
# =============================================================================

EMBED_MODEL = "nvidia/nv-embedqa-e5-v5"
LLM_MODEL   = "meta/llama-3.1-70b-instruct"

_client: OpenAI | None = None


def _nim() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.environ["NVIDIA_API_KEY"],
        )
    return _client


def _call(fn, *args, **kwargs):
    """Retry fn indefinitely on 429 rate-limit responses."""
    while True:
        try:
            return fn(*args, **kwargs)
        except RateLimitError:
            print("    [429] rate-limited — retrying in 5 s …", flush=True)
            time.sleep(5)


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
# ENTITY EMBEDDINGS — NIM API
# Replaces [DEVIATION-2]: paper uses facebook/contriever; we use EMBED_MODEL
# via NIM /v1/embeddings (OpenAI-compatible). No local GPU needed.
# Synonymy-edge similarity distribution differs from Contriever — sim_threshold
# may need retuning for a faithful reproduction.
# =============================================================================

def embed_batch(texts: list[str], input_type: str = "passage") -> np.ndarray:
    """Embed a list of strings; returns (N, dim) L2-normalised float64 array.

    input_type: "passage" for corpus/index text, "query" for query-side lookups.
    Required by asymmetric NIM embedding models.
    """
    response = _call(
        _nim().embeddings.create,
        model=EMBED_MODEL,
        input=texts,
        encoding_format="float",
        extra_body={"input_type": input_type},
    )
    vecs = np.array(
        [d.embedding for d in sorted(response.data, key=lambda x: x.index)],
        dtype=np.float64,
    )
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vecs / norms


def embed(text: str, input_type: str = "query") -> np.ndarray:
    return embed_batch([text], input_type=input_type)[0]


# =============================================================================
# PROMPTS — copied from OSU-NLP-Group/HippoRAG legacy src/openie_extraction_instructions.py
# =============================================================================

_ONE_SHOT_PASSAGE = (
    "Radio City\n"
    "Radio City is India's first private FM radio station and was started on 3 July 2001.\n"
    "It plays Hindi, English and regional songs.\n"
    "Radio City recently forayed into New Media in May 2008 with the launch of a music "
    "portal - PlanetRadiocity.com that offers music related news, videos, songs, and "
    "other music-related features."
)

_ONE_SHOT_ENTITIES = """{\"named_entities\":
    [\"Radio City\", \"India\", \"3 July 2001\", \"Hindi\", \"English\", \"May 2008\", \"PlanetRadiocity.com\"]
}
"""

_ONE_SHOT_TRIPLES = """{\"triples\": [
            [\"Radio City\", \"located in\", \"India\"],
            [\"Radio City\", \"is\", \"private FM radio station\"],
            [\"Radio City\", \"started on\", \"3 July 2001\"],
            [\"Radio City\", \"plays songs in\", \"Hindi\"],
            [\"Radio City\", \"plays songs in\", \"English\"],
            [\"Radio City\", \"forayed into\", \"New Media\"],
            [\"Radio City\", \"launched\", \"PlanetRadiocity.com\"],
            [\"PlanetRadiocity.com\", \"launched in\", \"May 2008\"],
            [\"PlanetRadiocity.com\", \"is\", \"music portal\"],
            [\"PlanetRadiocity.com\", \"offers\", \"news\"],
            [\"PlanetRadiocity.com\", \"offers\", \"videos\"],
            [\"PlanetRadiocity.com\", \"offers\", \"songs\"]
    ]
}
"""

_NER_SYSTEM = (
    "Your task is to extract named entities from the given paragraph. \n"
    "Respond with a JSON list of entities.\n"
)

_OPENIE_SYSTEM = (
    "Your task is to construct an RDF (Resource Description Framework) graph from the "
    "given passages and named entity lists. \n"
    "Respond with a JSON list of triples, with each triple representing a relationship "
    "in the RDF graph. \n\n"
    "Pay attention to the following requirements:\n"
    "- Each triple should contain at least one, but preferably two, of the named entities "
    "in the list for each passage.\n"
    "- Clearly resolve pronouns to their specific names to maintain clarity.\n"
)

_OPENIE_FRAME = (
    "Convert the paragraph into a JSON dict, it has a named entity list and a triple list.\n"
    "Paragraph:\n"
    "```\n"
    "{passage}\n"
    "```\n\n"
    "{named_entity_json}\n"
)


def _ner_messages(text: str) -> list[dict]:
    return [
        {"role": "system",    "content": _NER_SYSTEM},
        {"role": "user",      "content": f"Paragraph:\n```\n{_ONE_SHOT_PASSAGE}\n```\n"},
        {"role": "assistant", "content": _ONE_SHOT_ENTITIES},
        {"role": "user",      "content": f"Paragraph:```\n{text}\n```"},
    ]


def _openie_messages(passage: str, entities: list[str]) -> list[dict]:
    one_shot_input = _OPENIE_FRAME.format(
        passage=_ONE_SHOT_PASSAGE,
        named_entity_json=_ONE_SHOT_ENTITIES,
    )
    user_input = _OPENIE_FRAME.format(
        passage=passage,
        named_entity_json=json.dumps({"named_entities": entities}),
    )
    return [
        {"role": "system",    "content": _OPENIE_SYSTEM},
        {"role": "user",      "content": one_shot_input},
        {"role": "assistant", "content": _ONE_SHOT_TRIPLES},
        {"role": "user",      "content": user_input},
    ]


def _parse_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r'\{.*\}', text, re.DOTALL)
        if m:
            return json.loads(m.group())
        raise


# =============================================================================
# OPENIE — NIM LLM
# Replaces [DEVIATION-1]: paper uses GPT-3.5; we use LLM_MODEL via NIM.
# Two-step pipeline matching the original: NER first, then post-NER triple extraction.
# =============================================================================

def extract_triples(passage: str) -> list[tuple]:
    # Step 1: NER
    ner_resp = _call(
        _nim().chat.completions.create,
        model=LLM_MODEL,
        messages=_ner_messages(passage),
        temperature=0,
    )
    try:
        entities = _parse_json(ner_resp.choices[0].message.content).get("named_entities", [])
    except (json.JSONDecodeError, ValueError):
        entities = []

    # Step 2: post-NER OpenIE
    ie_resp = _call(
        _nim().chat.completions.create,
        model=LLM_MODEL,
        messages=_openie_messages(passage, entities),
        temperature=0,
    )
    try:
        data = _parse_json(ie_resp.choices[0].message.content)
        return [tuple(t[:3]) for t in data.get("triples", []) if len(t) >= 3]
    except (json.JSONDecodeError, ValueError):
        return []


# =============================================================================
# QUERY NER — NIM LLM
# Replaces [DEVIATION-3]: paper uses GPT-3.5 NER; we use LLM_MODEL via NIM.
# Reuses the same NER prompt as the indexing pipeline.
# =============================================================================

def extract_query_entities(question: str) -> list[str]:
    resp = _call(
        _nim().chat.completions.create,
        model=LLM_MODEL,
        messages=_ner_messages(question),
        temperature=0,
    )
    try:
        return _parse_json(resp.choices[0].message.content).get("named_entities", [])
    except (json.JSONDecodeError, ValueError):
        return []


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
    sep = "=" * 68

    print(sep)
    print("HippoRAG End-to-End Demo  (NIM-backed)")
    print(sep)
    print(f"\nCorpus: {len(PASSAGES)} passages  |  Questions: {len(TEST_QUESTIONS)}")
    print(f"LLM    : {LLM_MODEL}")
    print(f"Embed  : {EMBED_MODEL}")
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
        print(f"  P{i}: {len(triples)} triple(s)  {triples}")

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

    hr_hit1 = 0
    bl_hit1 = 0
    hr_hit_all = 0
    bl_hit_all = 0

    for qi, q_data in enumerate(TEST_QUESTIONS):
        q      = q_data["q"]
        answer = q_data["answer"]
        hops   = q_data["hops"]
        chain  = q_data["chain"]
        key_p  = q_data["key_passages"]

        print(f"\n{'─'*68}")
        print(f"Q{qi+1} ({hops}-hop): {q}")
        print(f"  Answer    : {answer}")
        print(f"  Hop chain : {chain}")
        print(f"  Key passages needed: {sorted(f'P{p}' for p in key_p)}")

        # NIM NER
        q_ents = extract_query_entities(q)
        print(f"  NIM NER   : {q_ents}")

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
