# Recipes for the HippoRAG reproduction demos.
# Install just from https://github.com/casey/just  (brew install just / apt install just).

default: help

help:
    @just --list

# Sync Python dependencies via uv (creates .venv).
sync:
    uv sync

# Run the HippoRAG (v1) demo — phrase-only KG, NER seeds, PPR × specificity.
demo:
    uv run python experiments/demo.py

# Run the HippoRAG 2 demo — phrase+passage KG, query→triple seeds with LLM filter.
demo-v2:
    uv run python experiments/demo_v2.py

# Run both demos back-to-back.
demo-all: demo demo-v2
