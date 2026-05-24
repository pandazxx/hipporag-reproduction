# Reproduction Notes — HippoRAG

*Working journal. Capture as it happens — don't polish. Goal is honest record, not pretty narrative.*

**Context:** see [`HANDOVER.md`](HANDOVER.md) for mission, constraints, definition of done.
**Study notes:** [`docs/paper-notes.md`](docs/paper-notes.md) (read before starting).

---

## Project log (chronological)

Format: one entry per session. Each entry stamps the date and one-line summary, then bullet details below.

### YYYY-MM-DD — Session 1 (template)

- (what got done)
- (what got tried)
- (what broke)
- (what was decided)

---

## Setup checklist

Things to confirm before doing real work:

- [ ] Read `docs/paper-notes.md` cover to cover
- [ ] Read `HANDOVER.md` cover to cover
- [ ] Decide which benchmark to use (MemoryAgentBench vs LongMemEval)
- [ ] OpenAI / Anthropic API key in `.env` (do NOT commit)
- [ ] Clone `OSU-NLP-Group/HippoRAG` `legacy` branch into `experiments/hipporag-original/` (gitignored)
- [ ] Pin the `openai<1.0` library version per the legacy repo's requirements
- [ ] Get one OpenIE call to succeed on a single test passage
- [ ] Identify and download a small (10–20 example) slice of the chosen benchmark

---

## What worked easily

*Things that just worked, no friction. Useful for the eventual reproduction report.*

- ...

## What was hard

*Setup pain, undocumented dependencies, broken scripts, version mismatches, environment errors. Capture even minor pains — they add up.*

- ...

## Deviations from the published methodology

*Where you had to substitute libraries, models, parameter values, or approaches. For each: what you changed, why, and what it could affect.*

| What was changed | Why | Possible downstream effect |
|---|---|---|
| | | |

---

## Cost log

Track API spend as you go. Don't trust your memory — note actual costs from the provider dashboards weekly.

| Date | What you ran | LLM model | Approx. tokens (in/out) | Cost (USD) | Cumulative |
|---|---|---|---|---|---|
| | | | | | |

**Budget reminder: $150 total. Escalate before exceeding.**

---

## Hyperparameters used

The non-obvious knobs and what you set them to.

| Hyperparameter | Default in legacy code | Value used | Reason if different |
|---|---|---|---|
| `sim_threshold` (synonymy cosine cutoff) | 0.8 | | |
| `damping` (PPR damping / 1-α teleport) | 0.1 | | |
| `node_specificity` (apply IDF weighting) | True | | |
| Max neighbours per entity for synonymy | 100 | | |
| LLM model for OpenIE | gpt-3.5-turbo | | |
| Embedding model | facebook/contriever | | |

---

## Final result on the small slice

Fill in after the end-to-end run.

| Metric | This reproduction | Published (paper benchmark) | Comment |
|---|---|---|---|
| Hits@1 / Recall@k / F1 | | | |
| Per-query latency | | | |
| Total API cost for slice | | | |
| Indexing time wall-clock | | | |

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

Things you wished the paper or code had explained.

- ...

## What I would do differently for a deeper reproduction

If the official project decides this becomes the real baseline (not just warmup), what changes.

- ...

## Hand-back summary

*Fill in when work is finished or abandoned. One paragraph.*

(Date: YYYY-MM-DD. Status: done / abandoned. Summary: ...)
