"""Loader + scoring helpers for the comparison dataset (dataset.json).

The dataset is mirrored from
https://github.com/pandazxx/research/tree/topic/further-research-e1e53be/topics/llm-agent-memory/comparison-dataset

It contains 40 memories (chronological) and 22 questions across 7 categories.
Each question lists `requires_facts` — the memory IDs (m01..m40) that must be
retrieved to answer it. A question with `requires_facts == []` is an
absence/abstention question that retrieval-only systems cannot score.
"""

import json
from collections import defaultdict
from pathlib import Path

DATASET_PATH = Path(__file__).parent / "dataset.json"


def load_dataset() -> dict:
    with DATASET_PATH.open() as f:
        return json.load(f)


def passages(ds: dict) -> list[str]:
    """Return memory contents in order; passage index == position in this list."""
    return [m["content"] for m in ds["memories"]]


def memory_id_to_idx(ds: dict) -> dict[str, int]:
    """Map memory IDs (e.g. 'm01') to passage indices."""
    return {m["id"]: i for i, m in enumerate(ds["memories"])}


def required_indices(question: dict, id_to_idx: dict[str, int]) -> set[int]:
    """Convert a question's requires_facts list to a set of passage indices."""
    return {id_to_idx[mid] for mid in question["requires_facts"] if mid in id_to_idx}


def category_expected_winners(ds: dict) -> dict[str, str]:
    """Map category -> expected winner (first occurrence wins; categories are coherent)."""
    out: dict[str, str] = {}
    for q in ds["questions"]:
        out.setdefault(q["category"], q["expected_winner"])
    return out


def score_retrieval(
    retrieved_top: list[int],
    required: set[int],
    top_k_any: int = 5,
    top_k_all: int = 10,
) -> tuple[bool | None, bool | None]:
    """Score a retrieval against the question's required facts.

    Returns (found_any, found_all). Both are None when required is empty
    (absence/abstention questions can't be scored from retrieval alone).
    """
    if not required:
        return None, None
    top_any = set(retrieved_top[:top_k_any])
    top_all = set(retrieved_top[:top_k_all])
    return bool(required & top_any), required.issubset(top_all)


def aggregate_by_category(
    per_question: list[dict],
) -> dict[str, dict[str, int]]:
    """Group per-question results by category.

    Each entry in per_question must have keys: category, found_any, found_all.
    found_any/found_all may be None for absence questions (counted as 'skipped').
    """
    out: dict[str, dict[str, int]] = defaultdict(
        lambda: {"hit_any": 0, "hit_all": 0, "total": 0, "skipped": 0}
    )
    for r in per_question:
        c = out[r["category"]]
        if r["found_any"] is None:
            c["skipped"] += 1
            continue
        c["total"] += 1
        c["hit_any"] += int(r["found_any"])
        c["hit_all"] += int(r["found_all"])
    return dict(out)


def format_summary(
    by_cat: dict[str, dict[str, int]],
    expected: dict[str, str],
    top_k_any: int = 5,
    top_k_all: int = 10,
) -> str:
    sep = "─" * 78
    lines = [
        f"{'Category':<28} {'Expected':<10} {f'Hit@{top_k_any}':>10} {f'All@{top_k_all}':>10}  Skip",
        sep,
    ]
    t_any = t_all = t_total = t_skip = 0
    for cat in sorted(by_cat.keys()):
        c = by_cat[cat]
        n = c["total"]
        exp = expected.get(cat, "?")
        if n == 0:
            lines.append(f"{cat:<28} {exp:<10} {'-':>10} {'-':>10}  {c['skipped']}")
        else:
            lines.append(
                f"{cat:<28} {exp:<10} "
                f"{c['hit_any']:>4}/{n:<2} ({c['hit_any']/n*100:>3.0f}%) "
                f"{c['hit_all']:>4}/{n:<2} ({c['hit_all']/n*100:>3.0f}%)  "
                f"{c['skipped']}"
            )
        t_any += c["hit_any"]
        t_all += c["hit_all"]
        t_total += n
        t_skip += c["skipped"]
    lines.append(sep)
    if t_total > 0:
        lines.append(
            f"{'TOTAL':<28} {'':<10} "
            f"{t_any:>4}/{t_total:<2} ({t_any/t_total*100:>3.0f}%) "
            f"{t_all:>4}/{t_total:<2} ({t_all/t_total*100:>3.0f}%)  "
            f"{t_skip}"
        )
    return "\n".join(lines)
