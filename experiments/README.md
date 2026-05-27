# Experiments

Two end-to-end demos running on the same 15-passage toy corpus and the same
four multi-hop questions, both backed by the NVIDIA NIM API. Layout:

- [`demo.py`](demo.py) — HippoRAG 1 (NeurIPS 2024, "legacy" branch)
- [`demo_v2.py`](demo_v2.py) — HippoRAG 2 (Feb 2025, "main" branch)
- [`_nim.py`](_nim.py) — shared NIM client + prompts (OpenIE, NER, recognition memory)

## Running

Both demos need `NVIDIA_API_KEY` set. The repo ships a `justfile` at the root
with shortcuts:

```bash
export NVIDIA_API_KEY=<your-key>
just sync         # uv sync — install deps once
just demo         # HippoRAG 1
just demo-v2      # HippoRAG 2
just demo-all     # run both back-to-back
```

Or invoke directly:

```bash
uv run python experiments/demo.py
uv run python experiments/demo_v2.py
```

Install `just` from https://github.com/casey/just (`brew install just` /
`apt install just`).

## What demo.py demonstrates (HippoRAG 1)

The v1 advantage on multi-hop questions: TF-IDF baseline can only match
passages whose words overlap the query, while HippoRAG follows entity chains
across passages via Personalized PageRank over a phrase-only KG.

| Phase | Step | Backed by |
|---|---|---|
| Indexing  | OpenIE (NER + post-NER triple extraction) | NIM LLM (`meta/llama-3.1-70b-instruct`) |
| Indexing  | Entity embedding                          | NIM embeddings (`nvidia/nv-embedqa-e5-v5`) |
| Indexing  | Synonymy edges (cosine ≥ 0.8)             | local numpy |
| Indexing  | KG construction + node specificity        | local |
| Retrieval | Query NER                                 | NIM LLM (broader prompt — extracts key concepts too) |
| Retrieval | Seed lookup (query → KG nodes)            | NIM embeddings + numpy argmax |
| Retrieval | Personalized PageRank                     | local scipy (power iteration) |
| Retrieval | Score passages by PPR × specificity       | local |

### Deviations from the paper

| ID | Paper | Demo | Status |
|---|---|---|---|
| DEVIATION-1 | OpenIE via GPT-3.5                  | OpenIE via NIM LLM             | Resolved |
| DEVIATION-2 | Embeddings via `facebook/contriever`| Embeddings via NIM             | Resolved |
| DEVIATION-3 | Query NER via GPT-3.5               | Query NER via NIM LLM (broader prompt) | Resolved |
| DEVIATION-4 | FAISS IndexFlat for nearest neighbour | Brute-force numpy dot       | Open |

The original HippoRAG NER + OpenIE prompts (verbatim from
`OSU-NLP-Group/HippoRAG@legacy:src/openie_extraction_instructions.py`) are used
for passage NER and triple extraction. A broader prompt is used for query NER
because questions often contain no classic named entities (e.g.
*"Who supervises the researcher working on quantum algorithms?"* — the only
useful retrieval anchor is the concept "quantum algorithms").

## What demo_v2.py demonstrates (HippoRAG 2)

HippoRAG 2 architectural changes on top of v1:

1. **Passage nodes in the graph.** Both phrase nodes (entities from triples)
   and passage nodes exist. Context edges link each phrase to the passage(s)
   it appears in.
2. **Query → triple linking.** Instead of NER on the query, v2 embeds the
   whole query and retrieves the top-K most similar *triples* (using
   `"subj pred obj"` as the triple text).
3. **Recognition memory.** An online LLM call filters those top-K triples
   down to the few relevant to the query. Phrases from the kept triples
   become high-weight PPR seeds; all passages also seed PPR at low weight,
   scaled by query↔passage embedding similarity.
4. **Ranking.** PPR scores read directly off the passage nodes — no node
   specificity weighting needed, because passages are now graph nodes.

| Phase | Step | Backed by |
|---|---|---|
| Indexing  | OpenIE (NER + post-NER triple extraction) | NIM LLM            |
| Indexing  | Embed phrases, passages, and triple texts | NIM embeddings     |
| Indexing  | Synonymy edges (cosine ≥ 0.75)            | local numpy        |
| Indexing  | Context edges (phrase ↔ passage)          | local              |
| Retrieval | Query → triple top-K (cosine)             | NIM embeddings     |
| Retrieval | Recognition memory (LLM filter ≤ 4)       | NIM LLM            |
| Retrieval | Personalized PageRank on combined graph   | local scipy        |
| Retrieval | Read PPR off passage nodes                | local              |

## Shared infrastructure

`_nim.py` exposes:

- `nim()` — lazily-created OpenAI-compatible client pointed at NIM
- `call(fn, ...)` — wraps every NIM call, retries indefinitely on HTTP 429
- `embed(text, input_type=...)` / `embed_batch(texts, ...)` — embeddings
  with mandatory `input_type` (asymmetric model)
- `extract_triples(passage)` — two-step OpenIE (NER + post-NER triples)
- `extract_query_entities(question)` — broader query NER (v1 only)
- `filter_triples(question, triples, top_k=4)` — recognition memory (v2 only)

Both demos use the same `EMBED_MODEL` (`nvidia/nv-embedqa-e5-v5`) and
`LLM_MODEL` (`meta/llama-3.1-70b-instruct`).

## Cost / rate limits

Free NIM tier: 1,000 credits on signup, 40 req/min. Wall-clock is dominated
by rate-limiting:

- v1 indexing: 30 LLM calls (15 passages × NER + OpenIE)
- v1 retrieval: ~1 LLM call per question (query NER) + a few embedding calls
- v2 indexing: same 30 OpenIE calls
- v2 retrieval: 1 LLM call per question (recognition filter) + a few embeddings

A single run of either demo stays well under 100 credits.

## See also

- [`../docs/nim-api-study.md`](../docs/nim-api-study.md) — feasibility study for
  the OpenAI→NIM and Contriever→NIM substitutions.
- [`../docs/paper-notes.md`](../docs/paper-notes.md) — consolidated notes on the
  HippoRAG paper.
