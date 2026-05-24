# experiments/demo.py

An end-to-end HippoRAG pipeline running on a 15-passage toy corpus, backed by
the NVIDIA NIM API. Compares HippoRAG retrieval against a TF-IDF baseline on
four multi-hop questions.

## What it demonstrates

The HippoRAG advantage on multi-hop questions: the baseline TF-IDF retriever
can only match passages whose words overlap the query, while HippoRAG follows
entity chains across passages via Personalized PageRank over the knowledge
graph.

## Pipeline

| Phase | Step | Backed by |
|---|---|---|
| Indexing | OpenIE (NER + post-NER triple extraction) | NIM LLM (`meta/llama-3.1-70b-instruct`) |
| Indexing | Entity embedding | NIM embeddings (`nvidia/nv-embedqa-e5-v5`) |
| Indexing | Synonymy edges (cosine ≥ 0.8) | local numpy |
| Indexing | KG construction + node specificity | local |
| Retrieval | Query NER | NIM LLM (broader prompt — extracts key concepts too) |
| Retrieval | Seed lookup (query → KG nodes) | NIM embeddings + numpy argmax |
| Retrieval | Personalized PageRank | local scipy (power iteration) |
| Retrieval | Score passages by PPR × specificity | local |

## Deviations from the paper

| ID | Paper | Demo | Status |
|---|---|---|---|
| DEVIATION-1 | OpenIE via GPT-3.5 | OpenIE via NIM LLM | Resolved |
| DEVIATION-2 | Embeddings via `facebook/contriever` | Embeddings via NIM | Resolved |
| DEVIATION-3 | Query NER via GPT-3.5 | Query NER via NIM LLM (broader prompt) | Resolved |
| DEVIATION-4 | FAISS IndexFlat for nearest neighbour | Brute-force numpy dot | Open |

The original NER prompt (copied verbatim from
`OSU-NLP-Group/HippoRAG@legacy:src/openie_extraction_instructions.py`) is used
for passage NER during indexing. A separate broader prompt is used for query NER
because questions often contain no classic named entities (e.g.
*"Who supervises the researcher working on quantum algorithms?"* — the only
useful retrieval anchor is the concept "quantum algorithms").

Synonymy threshold `sim_threshold=0.8` is the paper default but was calibrated
for Contriever embeddings; NIM `nv-embedqa-e5-v5` produces a different
similarity distribution and the threshold may need retuning for a faithful
reproduction.

Rate-limit handling: every NIM request is wrapped in `_call()` which retries
indefinitely on HTTP 429, sleeping 5 s between attempts. The free NIM tier is
40 req/min.

## Running

```bash
export NVIDIA_API_KEY=<your-key>
uv run python experiments/demo.py
```

`uv sync` will install the dependencies (`openai`, `numpy`, `scipy`, plus the
`langchain-nvidia-ai-endpoints` package that the demo doesn't currently use
but is staged in `pyproject.toml` for future LangChain integration).

Expected wall-clock: ~1 min depending on rate-limit behaviour. The OpenIE
phase makes 30 LLM calls (15 passages × 2 — NER then triple extraction);
retrieval makes 1 LLM call per question plus a handful of embedding calls.

## Output structure

```
Phase 1a — OpenIE  (NIM LLM)            triples printed per passage
Phase 1b — Indexing                     entity count, edge counts, embedding batch
Phase 2 — Retrieval                     per question:
                                          - NIM NER entities
                                          - HippoRAG top-5 with PPR scores
                                          - TF-IDF baseline top-5
                                          - hit indicator
Summary                                 hit@3 and hit-all@5 for both retrievers
```

## See also

- [`../docs/nim-api-study.md`](../docs/nim-api-study.md) — feasibility study for
  the OpenAI→NIM and Contriever→NIM substitutions.
- [`../docs/paper-notes.md`](../docs/paper-notes.md) — consolidated notes on the
  HippoRAG paper.
