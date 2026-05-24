# HippoRAG Reproduction

Reproduction of [HippoRAG (Gutiérrez et al., NeurIPS 2024)](https://arxiv.org/abs/2405.14831), a neurobiologically-inspired long-term memory system for LLMs that uses Personalized PageRank over a knowledge graph for retrieval.

This is a warmup / practice reproduction as part of a larger agent memory research project. The goal is **running, not matching published numbers exactly**.

## Status

🚧 Setup complete; reproduction work begins next.

**For the agent picking this up:** start with [`HANDOVER.md`](HANDOVER.md). That document contains the mission, constraints, definition of done, and recommended workflow.

**Reading order**:
1. [`HANDOVER.md`](HANDOVER.md) — mission and constraints
2. [`docs/paper-notes.md`](docs/paper-notes.md) — consolidated study of the HippoRAG paper
3. [`NOTES.md`](NOTES.md) — working journal (currently empty template; fill as you go)

## Goals

- Get the original HippoRAG pipeline running end-to-end on a small slice (10–20 examples) of [MemoryAgentBench](https://github.com/HUST-AI-HYZ/MemoryAgentBench) or [LongMemEval](https://github.com/xiaowu0162/LongMemEval).
- Document the reproduction process honestly: what was easy, what was hard, what would need to change for a deeper reproduction.
- Build the foundational understanding for downstream work on agent memory mechanisms.

## Original work

- **Paper:** https://arxiv.org/abs/2405.14831
- **Code:** https://github.com/OSU-NLP-Group/HippoRAG

## Approach

This repo is **not a fork** of the original HippoRAG. It pulls the original in as a dependency (via pip or as a git submodule). The structure here adds:

- `docs/` — reading notes, design observations.
- `experiments/` — scripts to run reproduction experiments.
- `results/` — logged benchmark numbers.
- `NOTES.md` — running journal of what was easy, what was hard.

## Timeline

Weeks 2–3 of the broader research project timeline. Hard cap: 10 working days. If genuinely stuck, the work is abandoned and documented (rather than allowed to consume the schedule indefinitely).

## License

MIT. See [LICENSE](LICENSE).
