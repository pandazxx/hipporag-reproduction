# Reproduction Notes — HippoRAG

*Working journal. Capture as it happens — don't polish. Goal is honest record, not pretty narrative.*

**Context:** see [`HANDOVER.md`](HANDOVER.md) for mission, constraints, definition of done.
**Study notes:** [`docs/paper-notes.md`](docs/paper-notes.md) (read before starting).

---

## Project log (chronological)

Format: one entry per session. Each entry stamps the date and one-line summary, then bullet details below.

### 2026-05-24 — Session 1: end-to-end demo (no API keys)

- Built `experiments/demo.py`: full HippoRAG pipeline from scratch using numpy + scipy only.
- Dataset: 15 hand-crafted passages about a fictional research lab; 4 multi-hop questions (2–3 hop).
- Triples specified manually (no LLM). Character trigram hashing used instead of Contriever for embeddings.
- PPR via scipy.sparse power iteration converges in <20 iterations on this graph.
- Result: HippoRAG 3/4 vs baseline 2/4 on "all key passages in top-5" metric.
- Key win: Q1 — HippoRAG finds the supervisor passage (P5) via graph traversal; TF-IDF baseline misses it.
- Key limit: 3-hop chains are hard; PPR signal too diluted by the time it reaches 3 hops.

---

## Setup checklist

Things to confirm before doing real work:

- [x] Read `docs/paper-notes.md` cover to cover
- [ ] Read `HANDOVER.md` cover to cover
- [ ] Decide which benchmark to use (MemoryAgentBench vs LongMemEval)
- [ ] OpenAI / Anthropic API key in `.env` (do NOT commit)
- [ ] Clone `OSU-NLP-Group/HippoRAG` `legacy` branch into `experiments/hipporag-original/` (gitignored)
- [ ] Pin the `openai<1.0` library version per the legacy repo's requirements
- [ ] Get one OpenIE call to succeed on a single test passage
- [ ] Identify and download a small (10–20 example) slice of the chosen benchmark

---

## What worked easily

- Implementing PPR from scratch with `scipy.sparse` power iteration matched the paper math exactly —
  convergence in <20 iterations for this tiny graph. No surprises.
- Core retrieval logic (seed → PPR → specificity weighting → passage scores) is ~60 lines of clean code.
- TF-IDF baseline easy to build; the contrast with HippoRAG is visible on multi-hop questions.
- The entity-to-passage map, node specificity formula, and P-matrix multiplication all translated
  directly from the paper into working code with no ambiguity.

## What was hard

- **No API keys available in the environment.** Cannot run LLM-based OpenIE or NER without providing a key.
  Demo uses manually specified triples and hard-coded query entities. Honest but limits realism.
- **Synonymy edges did not fire** on this small corpus. Character-trigram embeddings gave cosine < 0.8
  for all entity pairs, so the graph contains only triple edges. On a real corpus with Contriever,
  synonymy edges link e.g. "Alice" ↔ "Alice Chen" — a significant structural contribution.
- **3-hop chains are hard for PPR.** Q3 required Bob → Lab → Alice → Turing Award (3 hops).
  HippoRAG missed the Turing Award passage within top-5. The PPR teleport probability (α=0.15)
  dilutes signals beyond ~2 hops. 2-hop questions (Q1, Q4) showed clear advantage over baseline.

## Deviations from the published methodology

| Deviation | Paper | Demo (2026-05-24) | Impact |
|---|---|---|---|
| OpenIE | GPT-3.5 prompt | Manually specified triples | No extraction errors, but not automated |
| Entity embeddings | Contriever (768-dim dense) | Char trigram hashing (512-dim) | Synonymy edges did not fire (all pairs < 0.8 cosine) |
| Query NER | LLM call (1 per query) | Hard-coded query entities | Tests the PPR engine directly; skips NER step |
| ANN for synonymy | FAISS IndexFlat | Brute-force numpy O(N²) | Fine for N=16; would be slow at N=100K |
| Graph library | igraph (C, fast) | scipy.sparse power iteration | Same algorithm; fine at this scale |

---

## Cost log

Track API spend as you go. Don't trust your memory — note actual costs from the provider dashboards weekly.

| Date | What you ran | LLM model | Approx. tokens (in/out) | Cost (USD) | Cumulative |
|---|---|---|---|---|---|
| 2026-05-24 | demo.py (numpy + scipy, no API calls) | none | 0 / 0 | $0 | $0 |

**Budget reminder: $150 total. Escalate before exceeding.**

---

## Hyperparameters used

The non-obvious knobs and what you set them to.

| Hyperparameter | Default in legacy code | Value used | Reason if different |
|---|---|---|---|
| `sim_threshold` (synonymy cosine cutoff) | 0.8 | 0.8 | Same as paper |
| `damping` (PPR damping / 1-α teleport) | 0.1 | 0.15 | Slightly faster convergence; adjust when running on real corpus |
| `node_specificity` (apply IDF weighting) | True | True | Same as paper |
| Max neighbours per entity for synonymy | 100 | N/A (brute force) | No cap needed at N=16 |
| LLM model for OpenIE | gpt-3.5-turbo | none (manual triples) | No API key |
| Embedding model | facebook/contriever | char trigram hashing | No GPU / no torch |

---

## Final result on the small slice

Demo results (2026-05-24, 15 passages, 4 multi-hop questions, no API keys used):

| Metric | HippoRAG (demo) | Baseline TF-IDF | Published (paper) |
|---|---|---|---|
| ≥1 key passage in top-3 | 4/4 (100%) | 4/4 (100%) | — (different benchmark) |
| All key passages in top-5 | **3/4 (75%)** | 2/4 (50%) | — |
| Per-query latency | <1 ms (no LLM) | <1 ms | ~200–700 ms (LLM NER) |
| Total API cost | $0 | $0 | ~$5–15 (GPT-3.5, 5K passages) |

**Q1 (2-hop):** HippoRAG found the supervisor passage (P5) at rank 4 via graph traversal
(seed: "quantum algorithms" → Dr. Bob Martinez → Professor Alice Chen). Baseline missed P5
entirely because "supervised by" is not a keyword in the query.

**Q2 (2-hop):** Both methods found both key passages. TF-IDF keyword overlap was strong.

**Q3 (3-hop):** Neither method found all 3 key passages. HippoRAG found P4 and P0 but
missed P12 (Turing Award, 3 hops from seed). PPR signal diluted at 3+ hops.

**Q4 (2-hop):** HippoRAG found both key passages (P9 at rank 1, P10 at rank 3). Baseline
found both too (P10 at rank 4). Slight HippoRAG advantage.

If the metric doesn't match the published one one-to-one (e.g., different benchmark), say so explicitly.

---

## Comparison vs A-Mem

*To be filled in alongside the A-Mem reproduction in Week 4–5. Mirror columns must be filled in [`a-mem-reproduction/NOTES.md`](https://github.com/pandazxx/a-mem-reproduction/blob/main/NOTES.md).*

| Aspect | HippoRAG | A-Mem |
|---|---|---|
| Codebase quality | | |
| Setup difficulty | | |
| Documentation quality | | |
| Cost per evaluation (small slice) | | |
| Mental model (graph vs LLM-managed notes) | | |
| Most likely to be the project baseline | | |
| Things I would actually want to build on | | |

---

## Open questions raised during reproduction

- How much do synonymy edges actually contribute? The demo had zero synonymy edges. Are they load-bearing
  on real benchmarks, or just a minor complement to triple edges?
- Can PPR be tuned (lower alpha, more iterations) to reliably find 3-hop answers? Or is this a
  fundamental limitation that HippoRAG 2 addresses differently?
- What is the actual extraction error rate of GPT-3.5 OpenIE? The paper doesn't report this directly.
  How many triples are wrong, and what's the downstream impact on retrieval quality?

## What I would do differently for a deeper reproduction

- Get a real OpenAI API key and run the actual OpenIE + NER pipeline on a real benchmark slice.
- Use Contriever (local, CPU-only is feasible for N<10K) to get real synonymy edges.
- Test on the original benchmarks (MuSiQue, HotpotQA, 2WikiMultiHopQA) to compare with published numbers.
- Lower PPR alpha to 0.05 and test if 3-hop recall improves noticeably.

## Hand-back summary

*Fill in when work is finished or abandoned. One paragraph.*

(Date: YYYY-MM-DD. Status: done / abandoned. Summary: ...)
