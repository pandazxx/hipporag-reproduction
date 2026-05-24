# HippoRAG Reproduction — Handover

For the next agent picking this up. Read this top to bottom before starting.

---

## Mission

**Reproduce HippoRAG (Jiménez Gutiérrez et al., NeurIPS 2024) end-to-end on a small slice (10–20 examples) of a memory benchmark, in 10 working days.**

This is a **warmup**, not a serious reproduction. Goal is *running*, not *matching published numbers*. The work feeds two purposes simultaneously:
1. Practice — learn the reproduction workflow and tooling.
2. Information — produce concrete signal that informs the broader research project's direction decision.

---

## Project context

This work is **Week 2–3 of Phase 1A** of a 12.5-month agent memory research project. The project's master roadmap, decisions, and supporting research notes live in a separate repository:

- **Research repo (notes, surveys, roadmap):** https://github.com/pandazxx/research (see `topics/llm-agent-memory/`)
- **Project roadmap:** https://github.com/pandazxx/research/blob/topic/project-roadmap/topics/llm-agent-memory/project-roadmap.md
- **Sibling reproduction (A-Mem):** https://github.com/pandazxx/a-mem-reproduction — will happen in Week 4–5, *after* this one.

The two warmup reproductions feed a Week 5 direction decision between two candidate research mechanisms (reconsolidation vs active forgetting). Your output should make that decision easier — not by recommending the answer, but by documenting *what each codebase felt like to work with*.

---

## What has already been done

- [x] HippoRAG paper studied carefully. Consolidated study notes are at **[`docs/paper-notes.md`](docs/paper-notes.md)** — read this before touching code.
- [x] Repo scaffolded (README, NOTES.md, LICENSE, .gitignore, directory skeleton).
- [x] Direction agreed: reproduce **HippoRAG 1** (the original NeurIPS 2024 paper), not HippoRAG 2.
- [x] Branch identified: use the **`legacy`** branch of `OSU-NLP-Group/HippoRAG`. The `main` branch is HippoRAG 2 and is *not* the target.
- [x] Compute path agreed: API-only (Path A). No GPU needed.
- [x] Cost economics modelled — see `docs/paper-notes.md` for the detailed per-step cost tables.

---

## Definition of done

Warmup is complete when **all five** of these are true:

1. The HippoRAG legacy code (or a from-scratch reimplementation, if needed) runs end-to-end on at least 10 examples of MemoryAgentBench or LongMemEval, producing retrieved passages.
2. `NOTES.md` is populated with: setup pain points, codebase quality observations, deviations from the published methodology, cost log.
3. The reproduction's small-slice numbers (whatever they are — accuracy, F1, hit@k) are logged in `results/`.
4. A short Markdown writeup is in `docs/reproduction-report.md` answering: *"What did I learn from reproducing this? Would I want to build on this codebase?"*
5. The HippoRAG-vs-A-Mem comparison columns in [the sibling repo's `NOTES.md`](https://github.com/pandazxx/a-mem-reproduction/blob/main/NOTES.md) are filled in for the HippoRAG row (the A-Mem agent will fill the other row).

The numbers themselves do **not** need to match the published HippoRAG paper. If they're within an order of magnitude, that is sufficient signal for a warmup.

---

## Constraints

| Constraint | Value | Action if exceeded |
|---|---|---|
| **Time** | 10 working days (~2 calendar weeks) | After 5 days of being stuck on the same blocker, abandon. Document why in `NOTES.md` and submit early. |
| **Cost** | $150 budget for API calls | If approaching, switch to a cheaper model (GPT-3.5 → GPT-4o-mini) or shrink the slice. |
| **Scope** | Small slice, single benchmark | Do **not** try to reproduce all four benchmarks. Do **not** try to optimise hyperparameters. Do **not** add features. |
| **Quality** | "Just running" — not paper-matching | Resist the temptation to chase numbers. If it runs and produces sensible output, you are done. |

---

## Recommended workflow (rough)

| Day | Goal |
|---|---|
| 1 | Read `docs/paper-notes.md` end to end. Clone the `legacy` branch. Get past `pip install`. Get one OpenIE call working. |
| 2 | Identify the smallest viable test slice (10–20 examples from MemoryAgentBench or LongMemEval). Get OpenIE running over those passages. |
| 3 | Get the rest of the indexing pipeline working: entity dedup, embeddings, FAISS NN, KG construction, pickle. |
| 4 | Verify the index loads back correctly. Try a single query end-to-end. |
| 5 | Run the full small slice; log numbers. **Mid-warmup check-in:** if blocked, escalate or abandon. |
| 6 | Triage issues, run a second pass with one fix. |
| 7 | Fill out `NOTES.md` properly (codebase quality, deviations, cost log). |
| 8 | Write the reproduction report at `docs/reproduction-report.md`. |
| 9 | Buffer / unblocking time. |
| 10 | Final cleanup, commit, close out. |

---

## Decisions you can make autonomously

- Which LLM to use for OpenIE. **Recommend GPT-3.5 or GPT-4o-mini** for cost. Document the choice.
- Which embedding model to use. **Recommend the default Contriever** (`facebook/contriever`) for paper-faithfulness, but if it's a pain to set up, swap for OpenAI `text-embedding-3-large` and document the substitution.
- Specific benchmark slice (which 10–20 examples). Pick something representative; don't cherry-pick easy ones.
- Hyperparameter values where the paper is silent. Default to whatever's in the legacy repo's config.
- Whether to use the legacy code as-is, lightly modify it, or reimplement from scratch. **Recommend running the legacy code as-is** unless it's actively broken.

## Decisions to bring back to the user

- **Choice of benchmark** (MemoryAgentBench vs LongMemEval): default to LongMemEval since the paper used HotpotQA/MuSiQue which are closer in shape, but ask if you want to deviate.
- **Going past the $150 budget**: ask before spending more.
- **Going past 10 working days**: ask. Do not silently keep working.
- **Abandoning the warmup**: ask after documenting *why* you'd abandon. Don't drop it without surfacing the reasoning.
- **Reimplementing from scratch** if the legacy code is unusable: ask, since this changes the time budget materially.

---

## Where to find what

| Resource | Location |
|---|---|
| **Consolidated study notes** (read first) | [`docs/paper-notes.md`](docs/paper-notes.md) |
| **Working journal** (fill as you go) | [`NOTES.md`](NOTES.md) |
| **HippoRAG paper** | https://arxiv.org/abs/2405.14831 |
| **HippoRAG code (USE LEGACY BRANCH)** | https://github.com/OSU-NLP-Group/HippoRAG/tree/legacy |
| **HippoRAG 2 (NOT the target)** | https://github.com/OSU-NLP-Group/HippoRAG/tree/main |
| **Benchmark candidates** | MemoryAgentBench: https://github.com/HUST-AI-HYZ/MemoryAgentBench<br>LongMemEval: https://github.com/xiaowu0162/LongMemEval |
| **Project roadmap** | https://github.com/pandazxx/research/blob/topic/project-roadmap/topics/llm-agent-memory/project-roadmap.md |
| **Embedding-provider deep dive** (if you need to swap embedders) | https://github.com/pandazxx/research/blob/topic/further-research-e1e53be/topics/llm-agent-memory/commercial-embeddings-deep-dive.md |
| **Cost tables** (per-step API/CPU/GPU breakdown) | inside `docs/paper-notes.md`, sections "Indexing cost breakdown" and "Per-query cost breakdown" |

---

## Critical gotchas

1. **Use the `legacy` branch.** The `main` branch is HippoRAG 2, a *different* system with different architecture (passage-as-node, more online LLM use). Do not mix them.
2. **OpenIE setup is the most likely failure point.** The legacy repo uses OpenAI's GPT-3.5 via the deprecated `openai<1.0` API. You may need to update the calling convention or pin the old version. Document whatever you do.
3. **The `inter_triple_weight` and `similarity_max` constants are both 1.0** in the original code (`create_graph.py` lines 20–21). You do not need to tune them — but be aware of the unit mismatch they create (see `docs/paper-notes.md`, "Design choices and implications").
4. **Predicates are discarded** during graph construction. If you are tempted to use them, you are deviating from the paper — document the deviation explicitly.
5. **Synonymy edges depend on the embedding model.** If you swap models, expect different downstream numbers. This is *expected* deviation, not a bug.
6. **OpenIE is the cost bottleneck.** Parallelise it (the legacy repo has `openie_with_retrieval_option_parallel.py`). Do not run it sequentially or you will burn an entire day on indexing 5,000 passages.

---

## What to do if stuck

A "stuck" situation lasting more than 1 day should be escalated. After 5 days of being stuck on the same blocker, abandon the warmup and document the failure.

A productive escalation includes:
- What exactly is failing (concrete error message, expected vs actual)
- What you have tried (3+ approaches if it has been more than a day)
- A specific question or decision needed from the user
- An estimate of how much time has been spent on this blocker

A *non-productive* escalation is "stuck, please help" — that wastes the user's time.

---

## Reporting back

Continuously, as you work:
- Update `NOTES.md` with what is happening. Don't polish — capture.
- Commit early and often. Even broken intermediate states are useful (rollback is cheap, lost work is not).

At the end (or on early abandon):
- Make sure all five "definition of done" items are addressed.
- Write `docs/reproduction-report.md` (1–2 pages).
- Push, then surface to the user with a one-paragraph summary: what you got working, what you didn't, what surprised you.

---

## What you should *not* do

Out of scope for this warmup, no matter how tempting:
- Don't reproduce HippoRAG 2.
- Don't run more than one benchmark.
- Don't tune hyperparameters past the published defaults.
- Don't write your own variant of HippoRAG (that's the main project, not the warmup).
- Don't worry about engineering quality, tests, or production-ready code. Quick, ugly, working code is correct here.
- Don't make the README pretty (yet). That happens after the warmup, when the reproduction is settled.
- Don't add features, refactor, or "clean up" the legacy code beyond what's needed to make it run.

If you finish in less than 10 days, do not start any of the above. Stop, write the report, hand back to the user.
