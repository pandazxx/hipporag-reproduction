"""Mermaid renderers for the memory graph and per-query search traces.

Writes Markdown files (with embedded mermaid blocks) to a results directory.
Mermaid was picked over Graphviz/HTML because it (a) renders inline on GitHub
and most markdown viewers, (b) is plain text so diffs and reviews work, and
(c) requires no extra runtime tooling.
"""

from pathlib import Path

import numpy as np


def _esc(s: str) -> str:
    """Escape a label for mermaid node text."""
    return (s.replace('"', "'")
             .replace("\n", " ")
             .replace("[", "(")
             .replace("]", ")"))


def _truncate(s: str, n: int = 50) -> str:
    return s if len(s) <= n else s[:n] + "…"


# =============================================================================
# Memory-graph overview
# =============================================================================

def render_index_overview(
    index: dict,
    version: str,
    memory_ids: list[str],
    passages: list[str],
    max_phrases: int = 30,
) -> str:
    """Render the indexed memory graph as a markdown overview.

    Works for both v1 (uses index["entities"], index["P_matrix"]) and v2
    (uses index["phrases"], index["N_phrase"], index["adj"]).
    """
    is_v2 = "phrases" in index

    if is_v2:
        phrases = index["phrases"]
        N_phrase = index["N_phrase"]
        adj_full = index["adj"].toarray()
        adj_phrase = adj_full[:N_phrase, :N_phrase]
    else:
        phrases = index["entities"]
        N_phrase = len(phrases)
        adj_phrase = index["adj"].toarray()

    if N_phrase == 0:
        return f"# {version} index — empty graph\n"

    # Pick top-N phrases by degree for the diagram
    degree = (adj_phrase > 0).sum(axis=1)
    top_idx = np.argsort(-degree)[:max_phrases]
    top_set = {int(i) for i in top_idx}

    lines = [
        f"# {version} memory graph",
        "",
        f"- **Memories indexed:** {len(passages)}",
        f"- **Phrase nodes:** {N_phrase}",
    ]
    if is_v2:
        lines.append(f"- **Passage nodes:** {index['P']}")
        lines.append(f"- **Total graph nodes:** {index['N']}")
        lines.append(f"- **Triples extracted:** {len(index['triples'])}")
    lines.extend([
        "",
        f"## Phrase subgraph (top {min(max_phrases, N_phrase)} of {N_phrase} by degree)",
        "",
        "Shows relation + synonymy edges among the most-connected phrases. "
        "Passage and context edges are omitted for clarity.",
        "",
        "```mermaid",
        "graph LR",
    ])
    # Nodes
    for i in top_idx:
        i = int(i)
        lines.append(f'    n{i}["{_esc(phrases[i])}"]')
    # Edges (phrase ↔ phrase, only between shown nodes)
    for i in top_idx:
        i = int(i)
        for j in top_idx:
            j = int(j)
            if i >= j:
                continue
            if adj_phrase[i, j] > 0:
                lines.append(f"    n{i} --- n{j}")
    lines.append("```")

    # Top phrases by degree as a table
    lines.extend([
        "",
        "## Top phrases by degree",
        "",
        "| Rank | Phrase | Degree |",
        "|---|---|---|",
    ])
    for rank, i in enumerate(top_idx[:20], 1):
        i = int(i)
        lines.append(f"| {rank} | `{phrases[i]}` | {int(degree[i])} |")

    return "\n".join(lines) + "\n"


# =============================================================================
# Per-query traces
# =============================================================================

def render_v1_trace(
    question: dict,
    trace: dict,
    index: dict,
    memory_ids: list[str],
    passages: list[str],
    required: set[int],
    top_phrases_to_show: int = 10,
) -> str:
    """Render a HippoRAG v1 query trace.

    `trace` must contain:
      - q_ents: list[str] — extracted query entities
      - seed_lookups: list[(qe, matched_phrase, sim)]
      - seed_indices: list[int]
      - weighted: ndarray (N_phrase,) — PPR × specificity
      - top_passages: list[(pidx, score)]
    """
    entities = index["entities"]
    N_phrase = len(entities)
    adj = index["adj"].toarray()
    P_matrix = index["P_matrix"].toarray()  # (N_phrase, P)

    seed_set = set(trace["seed_indices"])
    weighted = trace["weighted"]

    # Pick top phrases by weighted score (excluding seeds themselves so we see propagation)
    non_seed_mask = np.ones(N_phrase, dtype=bool)
    non_seed_mask[list(seed_set)] = False
    masked = np.where(non_seed_mask, weighted, -1.0)
    top_phrase_idx = [int(i) for i in np.argsort(-masked)[:top_phrases_to_show] if masked[i] > 0]

    shown = list(seed_set) + top_phrase_idx
    top_passages = trace["top_passages"][:5]
    top_pset = {pidx for pidx, _ in top_passages}

    lines = [
        f"# Trace — {question['id']}  [{question['category']}, expect={question['expected_winner']}]",
        "",
        f"**Question:** {question['question']}",
        "",
        f"**Expected answer:** {question['expected_answer']}",
        "",
        f"**Required facts:** {question['requires_facts'] or '(none — absence/abstention)'}",
        "",
        f"**Query NER:** `{trace['q_ents']}`",
        "",
        "## Seed lookups (query entity → KG phrase)",
        "",
    ]
    if trace["seed_lookups"]:
        lines.append("| Query entity | Matched phrase | Cosine |")
        lines.append("|---|---|---|")
        for qe, phrase, sim in trace["seed_lookups"]:
            lines.append(f"| `{qe}` | `{phrase}` | {sim:.3f} |")
    else:
        lines.append("_(no seeds — query NER returned nothing)_")
    lines.append("")

    lines.append("## Top 5 retrieved passages")
    lines.append("")
    lines.append("| Rank | Memory | Score | Hit | Text |")
    lines.append("|---|---|---|---|---|")
    for rank, (pidx, score) in enumerate(top_passages, 1):
        hit = "✓" if pidx in required else ""
        lines.append(f"| {rank} | `{memory_ids[pidx]}` | {score:.5f} | {hit} | {_truncate(passages[pidx], 60)} |")
    lines.append("")

    lines.append("## Search subgraph")
    lines.append("")
    lines.append("Seeds (red), top-PPR phrases (blue), top-5 passages "
                 "(green if required, grey otherwise).")
    lines.append("")
    lines.append("```mermaid")
    lines.append("graph LR")

    # Phrase nodes
    for i in seed_set:
        lines.append(f'    n{i}(["{_esc(entities[i])}"]):::seed')
    for i in top_phrase_idx:
        lines.append(f'    n{i}["{_esc(entities[i])}"]:::phrase')

    # Passage nodes
    for pidx, score in top_passages:
        mid = memory_ids[pidx]
        cls = "hit" if pidx in required else "passage"
        label = f"{mid}: {_truncate(passages[pidx], 35)}"
        lines.append(f'    p{pidx}["{_esc(label)}"]:::{cls}')

    # Phrase-phrase edges (within shown set)
    seen = set()
    for i in shown:
        for j in shown:
            if i >= j:
                continue
            if adj[i, j] > 0 and (i, j) not in seen:
                lines.append(f"    n{i} --- n{j}")
                seen.add((i, j))

    # Phrase-passage edges (P_matrix), only between shown phrases and top passages
    for i in shown:
        for pidx in top_pset:
            if P_matrix[i, pidx] > 0:
                lines.append(f"    n{i} -.-> p{pidx}")

    lines.append("    classDef seed fill:#fdd,stroke:#c44,stroke-width:2px")
    lines.append("    classDef phrase fill:#eef,stroke:#446")
    lines.append("    classDef passage fill:#f5f5f5,stroke:#666")
    lines.append("    classDef hit fill:#dfd,stroke:#080,stroke-width:3px")
    lines.append("```")

    return "\n".join(lines) + "\n"


def render_v2_trace(
    question: dict,
    trace: dict,
    index: dict,
    memory_ids: list[str],
    passages: list[str],
    required: set[int],
    top_phrases_to_show: int = 10,
) -> str:
    """Render a HippoRAG 2 query trace.

    `trace` must contain:
      - top_triples: list[(subj, pred, obj, sim)]
      - filtered_triples: list[(subj, pred, obj)]
      - ppr_scores: ndarray (N,)
      - top_passages: list[(pidx, score)]
    """
    phrases = index["phrases"]
    phrase_idx = index["phrase_idx"]
    N_phrase = index["N_phrase"]
    adj = index["adj"].toarray()

    # Seeds = phrases referenced by filtered triples
    seed_set: set[int] = set()
    for s, _p, o in trace["filtered_triples"]:
        if s in phrase_idx:
            seed_set.add(phrase_idx[s])
        if o in phrase_idx:
            seed_set.add(phrase_idx[o])

    # Top phrases by PPR (excluding seeds)
    ppr_phrase = trace["ppr_scores"][:N_phrase]
    non_seed_mask = np.ones(N_phrase, dtype=bool)
    if seed_set:
        non_seed_mask[list(seed_set)] = False
    masked = np.where(non_seed_mask, ppr_phrase, -1.0)
    top_phrase_idx = [int(i) for i in np.argsort(-masked)[:top_phrases_to_show] if masked[i] > 0]

    shown = list(seed_set) + top_phrase_idx
    top_passages = trace["top_passages"][:5]
    top_pset = {pidx for pidx, _ in top_passages}

    lines = [
        f"# Trace — {question['id']}  [{question['category']}, expect={question['expected_winner']}]",
        "",
        f"**Question:** {question['question']}",
        "",
        f"**Expected answer:** {question['expected_answer']}",
        "",
        f"**Required facts:** {question['requires_facts'] or '(none — absence/abstention)'}",
        "",
        "## Step 1 — query→triple top-K (cosine on triple-text embeddings)",
        "",
    ]
    if trace["top_triples"]:
        lines.append("| Cosine | Subject | Predicate | Object |")
        lines.append("|---|---|---|---|")
        for s, p, o, sim in trace["top_triples"]:
            lines.append(f"| {sim:.3f} | `{s}` | {p} | `{o}` |")
    else:
        lines.append("_(no triples in index)_")
    lines.append("")

    lines.append("## Step 2 — recognition memory (LLM filter)")
    lines.append("")
    if trace["filtered_triples"]:
        lines.append("| Subject | Predicate | Object |")
        lines.append("|---|---|---|")
        for s, p, o in trace["filtered_triples"]:
            lines.append(f"| `{s}` | {p} | `{o}` |")
    else:
        lines.append("_(LLM kept no triples)_")
    lines.append("")

    lines.append("## Step 3 — top 5 retrieved passages")
    lines.append("")
    lines.append("| Rank | Memory | PPR | Hit | Text |")
    lines.append("|---|---|---|---|---|")
    for rank, (pidx, score) in enumerate(top_passages, 1):
        hit = "✓" if pidx in required else ""
        lines.append(f"| {rank} | `{memory_ids[pidx]}` | {score:.5f} | {hit} | {_truncate(passages[pidx], 60)} |")
    lines.append("")

    lines.append("## Search subgraph")
    lines.append("")
    lines.append("Seeds from filtered triples (red), top-PPR phrases (blue), "
                 "top-5 passage nodes (green if required, grey otherwise).")
    lines.append("")
    lines.append("```mermaid")
    lines.append("graph LR")

    for i in seed_set:
        lines.append(f'    n{i}(["{_esc(phrases[i])}"]):::seed')
    for i in top_phrase_idx:
        lines.append(f'    n{i}["{_esc(phrases[i])}"]:::phrase')

    for pidx, _score in top_passages:
        node_idx = N_phrase + pidx
        mid = memory_ids[pidx]
        cls = "hit" if pidx in required else "passage"
        label = f"{mid}: {_truncate(passages[pidx], 35)}"
        lines.append(f'    g{node_idx}["{_esc(label)}"]:::{cls}')

    # Phrase ↔ phrase edges
    seen = set()
    for i in shown:
        for j in shown:
            if i >= j:
                continue
            if adj[i, j] > 0 and (i, j) not in seen:
                lines.append(f"    n{i} --- n{j}")
                seen.add((i, j))

    # Phrase ↔ passage context edges
    for i in shown:
        for pidx in top_pset:
            node_idx = N_phrase + pidx
            if adj[i, node_idx] > 0:
                lines.append(f"    n{i} -.-> g{node_idx}")

    lines.append("    classDef seed fill:#fdd,stroke:#c44,stroke-width:2px")
    lines.append("    classDef phrase fill:#eef,stroke:#446")
    lines.append("    classDef passage fill:#f5f5f5,stroke:#666")
    lines.append("    classDef hit fill:#dfd,stroke:#080,stroke-width:3px")
    lines.append("```")

    return "\n".join(lines) + "\n"


# =============================================================================
# Output directory management
# =============================================================================

def prepare_output_dir(version: str) -> Path:
    """Create results/<version>/ and clear stale trace files. Returns the path."""
    out = Path("results") / version
    out.mkdir(parents=True, exist_ok=True)
    for stale in out.glob("q*_trace.md"):
        stale.unlink()
    return out
