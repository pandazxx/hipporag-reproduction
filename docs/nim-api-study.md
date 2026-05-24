# NVIDIA NIM API — Feasibility Study for HippoRAG Reproduction

**Branch:** `topic/nim-api-study`
**Date:** 2026-05-24
**Question:** Can NVIDIA NIM replace the OpenAI LLM calls and the Contriever (HuggingFace) embedding calls in the HippoRAG legacy codebase?

**Verdict: Yes — both replacements are feasible and low-effort.**

---

## What the legacy code actually calls

Three distinct external services are used:

| Role | Default | Called from |
|---|---|---|
| OpenIE / NER (LLM) | OpenAI `gpt-3.5-turbo-1106` | `src/langchain_util.py` → `init_langchain_model()` |
| Query entity linking (embeddings) | `facebook/contriever` via HuggingFace | `src/lm_wrapper/util.py` → `init_embedding_model()` |
| QA reader (LLM) | OpenAI `gpt-3.5-turbo` | `hipporag.py:132` — same `init_langchain_model()` |

The embedding path (`init_embedding_model`) dispatches on the model name string: GritLM names go to `GritWrapper`, everything else goes to `HuggingFaceWrapper`, which loads the model locally using `transformers.AutoModel` and requires CUDA. There is no API-based embedding path in the legacy code.

---

## What NVIDIA NIM offers

### LLM endpoint

- Base URL: `https://integrate.api.nvidia.com/v1`
- Endpoint: `POST /v1/chat/completions` — fully OpenAI-compatible
- Auth: `NVIDIA_API_KEY` env var
- Models relevant to this project: Llama 3.1-70B, Llama 3.3-70B, Mistral, Qwen3, DeepSeek, NVIDIA Nemotron, Phi-4
- LangChain package: `langchain-nvidia-ai-endpoints` → `ChatNVIDIA`
- **Free tier:** 1,000 credits on signup; 40 req/min rate limit

### Embedding endpoint

- Same base URL: `https://integrate.api.nvidia.com/v1`
- Endpoint: `POST /v1/embeddings` — OpenAI-compatible
- Models: `nvidia/nv-embedqa-e5-v5`, `nvidia/llama-3.2-nemoretriever-300m-embed-v1`, `NV-Embed-QA`, `nvidia/llama-3.2-nv-embedqa-1b-v2`
- Also available via LangChain: `NVIDIAEmbeddings`
- No local GPU required — pure API call

---

## Replacement 1: LLM (OpenAI → NIM)

### Where to change

`src/langchain_util.py`, `init_langchain_model()`. The function is a simple `if/elif` dispatcher. Adding NIM is one new branch:

```python
elif llm == 'nim':
    from langchain_nvidia_ai_endpoints import ChatNVIDIA
    return ChatNVIDIA(
        model=model_name,
        temperature=temperature,
        max_retries=max_retries,
        **kwargs
    )
```

Then invoke HippoRAG with `--llm nim --model_name meta/llama-3.1-70b-instruct`.

### One gotcha — JSON mode check

`openie_with_retrieval_option_parallel.py` checks `isinstance(client, ChatOpenAI)` to decide whether to request `response_format={"type": "json_object"}`. `ChatNVIDIA` is not `ChatOpenAI`, so it falls into the `else` branch which calls `extract_json_dict()` on raw output — this already works for non-OpenAI providers (Together, Ollama). Safe.

### One gotcha — token usage accounting

The OpenIE script reads `chat_completion.response_metadata['token_usage']['total_tokens']`. LangChain's `ChatNVIDIA` populates `response_metadata` similarly to `ChatOpenAI`, so this should work. Needs one quick test call to verify.

### Effort estimate

~5 lines in `langchain_util.py`. Zero changes elsewhere.

---

## Replacement 2: Embeddings (Contriever/HuggingFace → NIM)

### Where to change

`src/lm_wrapper/util.py`, `init_embedding_model()`. Currently dispatches:
- `GritLM/` prefix → `GritWrapper` (local GPU)
- anything else → `HuggingFaceWrapper` (local GPU, needs `device='cuda'`)

A new `NIMEmbeddingWrapper` needs to implement the same interface as `HuggingFaceWrapper`:
- `encode_text(text, ..., return_numpy=False)` → returns numpy array of shape `(N, dim)`
- `get_query_doc_scores(query_vec, doc_vecs)` → dot product (already in base class)

Dispatch trigger: add an `elif model_name.startswith('nim/')` (or `'nvidia/'`) branch.

### Minimal implementation sketch

```python
# src/lm_wrapper/nim_util.py
import numpy as np
from openai import OpenAI
from src.lm_wrapper import EmbeddingModelWrapper

class NIMEmbeddingWrapper(EmbeddingModelWrapper):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model_name_processed = model_name.replace('/', '_')
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.environ["NVIDIA_API_KEY"],
        )

    def encode_text(self, text, instruction=None, norm=True, return_cpu=False, return_numpy=False):
        if isinstance(text, str):
            text = [text]
        response = self.client.embeddings.create(
            model=self.model_name,
            input=text,
            encoding_format="float",
        )
        vecs = np.array([d.embedding for d in response.data], dtype=np.float32)
        if norm:
            vecs = vecs / np.linalg.norm(vecs, axis=1, keepdims=True)
        return vecs

    def get_query_doc_scores(self, query_vec, doc_vecs):
        return np.dot(doc_vecs, query_vec.T)
```

Then in `init_embedding_model()`:
```python
elif model_name.startswith('nvidia/') or model_name.startswith('nim/'):
    from src.lm_wrapper.nim_util import NIMEmbeddingWrapper
    return NIMEmbeddingWrapper(model_name)
```

Call with `graph_creating_retriever_name='nvidia/nv-embedqa-e5-v5'`.

### Effort estimate

~50 lines, one new file, two-line change to `init_embedding_model()`.

---

## Deviation from the paper

Replacing Contriever with a NIM embedding model is a **documented deviation**. Effects:

| Property | Contriever (`facebook/contriever`) | NIM (`nvidia/nv-embedqa-e5-v5`) |
|---|---|---|
| Max input tokens | 128 | 512 (e5-v5), 8192 (NemoRetriever-300M) |
| Training objective | Contrastive (unsupervised) | Supervised retrieval (QA-optimized) |
| Cosine similarity distribution | Different baseline | Different baseline |
| Synonymy threshold `0.8` | Calibrated for Contriever | May need retuning |

This is expected deviation for a warmup. Log the substitution in `NOTES.md`.

---

## Recommended model choices

| Role | Recommended NIM model | Rationale |
|---|---|---|
| OpenIE / NER LLM | `meta/llama-3.1-70b-instruct` | Best open-weight balance; known good at JSON extraction |
| Embedding (synonymy + linking) | `nvidia/nv-embedqa-e5-v5` | General-purpose dense retriever; closest to Contriever in design |
| QA reader (if needed) | `meta/llama-3.1-8b-instruct` | Cheaper; QA reading is easier than OpenIE |

Avoid `nvidia/llama-3.2-nemoretriever-300m-embed-v1` for indexing — it is optimised for QA passage retrieval, not synonymy detection.

---

## Cost on free tier

For a 10–20 example run:
- OpenIE: ~20 passages × ~300 tokens output ≈ 6,000 output tokens → well within free credits
- Embeddings: ~200 entity phrases × 1 call → trivial
- Full run should consume < 50 credits out of 1,000

**No budget risk on the free tier for the warmup slice.**

---

## Required package change

Add to `pyproject.toml` dependencies:

```toml
"langchain-nvidia-ai-endpoints>=0.3",
```

And the new `NIMEmbeddingWrapper` only needs `openai` (already in deps) — no extra package.

---

## Summary

Both replacements are go. LLM swap is 5 lines; embedding swap is ~50 lines. No GPU needed. Free-tier credits cover the entire warmup slice. The only non-trivial issue is verifying that `ChatNVIDIA` populates `response_metadata['token_usage']` — worth a one-call smoke test before the full run.
