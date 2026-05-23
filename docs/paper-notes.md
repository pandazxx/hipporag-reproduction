# HippoRAG — Paper Study Notes

Consolidated notes from reading *HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models* (Jiménez Gutiérrez et al., NeurIPS 2024).

Paper: https://arxiv.org/abs/2405.14831
Code: https://github.com/OSU-NLP-Group/HippoRAG (legacy branch is the original paper)

---

## TL;DR

HippoRAG is a retrieval system that replaces vanilla dense retrieval with a **knowledge-graph-plus-Personalized-PageRank** approach. An LLM is used during indexing to extract (subject, predicate, object) triples from each passage; the entities become nodes, the triples become edges. At query time the system extracts query entities, matches them to KG nodes, and runs Personalized PageRank to propagate relevance through the graph. Top passages are scored by combining PPR scores with node specificity (an IDF-like weighting).

The headline claim: this approach handles **multi-hop questions** much better than vanilla dense retrieval because graph propagation can follow chains of relations across passages, while dense retrieval just finds passages similar to the query text.

---

## Brain inspiration

The paper draws on the **hippocampal memory indexing theory** from neuroscience: the hippocampus stores compact indices that link to richer detail stored in the neocortex.

Mapping the paper uses:

| Brain | HippoRAG component |
|---|---|
| Hippocampus | The knowledge graph (the index) |
| Neocortex | The original passages (the detailed content) |
| Pattern separation | Entity-based indexing — distinct entities get distinct nodes |
| Pattern completion | PPR propagation — partial cues activate the full memory |

The analogy is loose but pedagogically useful. The paper's real contribution is the engineering combination, not a faithful brain model.

---

## Architecture overview

Two phases:

1. **Offline indexing** (run once per corpus, expensive): build the knowledge graph and supporting matrices.
2. **Online retrieval** (per query, cheap): extract query entities, run PPR, return top passages.

The key economic insight: HippoRAG **front-loads LLM cost into indexing**, then queries are cheap. Compare to iterative retrieval methods (IRCoT) that do many LLM calls per query.

---

## Phase 1 — Offline indexing

Step by step:

1. **OpenIE on every passage.** Use an LLM (GPT-3.5 in the paper) to extract (subject, predicate, object) triples from each passage.
2. **Entity deduplication.** Collect unique entities across all triples. Each becomes a node.
3. **Build the entity-to-passage map.** Track which passages each entity appears in (this becomes the `P` matrix).
4. **Encode every entity.** Compute embedding for each entity using a retriever model (default: Contriever, also supports ColBERTv2).
5. **Compute all-pairs nearest neighbours.** Use FAISS with `IndexFlat` + `METRIC_INNER_PRODUCT` over L2-normalised embeddings = cosine similarity. Save top-k (k=2047) per entity.
6. **Build the knowledge graph.** Add edges of two types (described below). Combine into a single dictionary `graph_plus`.
7. **Compute node specificity.** For each node, store 1/(passage count containing this entity).
8. **Pickle everything.** Save the graph, the P matrix, entity embeddings, node specificities.

**Cost profile:** dominated by step 1 (OpenIE). Roughly 1 LLM call per passage. At API rates, ~$0.01–$0.10 per passage; indexing 5,000 passages costs ~$50–$200.

---

## Phase 2 — Online retrieval

Step by step:

1. **Query NER.** LLM call to extract named entities from the query.
2. **Match query entities to KG nodes.** For each extracted entity, find nearest KG nodes by cosine similarity to entity embeddings.
3. **Build personalisation vector `s`.** Uniform probability over matched nodes; zero elsewhere.
4. **Run Personalized PageRank.** Iterate to convergence over the precomputed graph using `s`. Result: distribution over all nodes.
5. **Apply node specificity.** Multiply each node's PPR score by its precomputed specificity.
6. **Compute passage scores.** Multiply by the `P` matrix: `p = (n_specificity_weighted)ᵀ · P`.
7. **Return top-K passages by score.**

**Cost profile:** one LLM call (step 1, the NER). PPR itself is tens of milliseconds for ~100K-node graphs. Total per-query cost is dominated by the LLM call.

---

## Components in detail

### OpenIE — Open Information Extraction

The task of extracting (subject, predicate, object) triples from natural-language text without a fixed schema.

Example:
- Input: *"Albert Einstein was born in Ulm in 1879."*
- Output:
  - `(Albert Einstein, was born in, Ulm)`
  - `(Albert Einstein, was born in, 1879)`

HippoRAG uses an LLM (GPT-3.5) for OpenIE rather than legacy systems (Stanford OpenIE, ReVerb). The LLM is more accurate but more expensive.

**Crucial detail: the predicate is discarded** when building the graph. Only the entities matter. This makes HippoRAG robust to wrong-predicate extraction but loses semantic precision (cannot distinguish "Alice studies under Thomas" from "Alice fired Thomas" — same edge results).

### The knowledge graph

- **Nodes**: unique entities (subjects or objects from OpenIE triples).
- **Two edge types**, both stored in a single dictionary `graph_plus[(node_i, node_j)] = weight`:
  - `E` — triple-based edges
  - `E→` — synonymy edges

### Triple edges (E)

```python
graph[fact_edge_r] = graph.get(fact_edge_r, 0.0) + inter_triple_weight  # = 1.0
graph[fact_edge_l] = graph.get(fact_edge_l, 0.0) + inter_triple_weight
```

- Weight = **co-occurrence count** (number of triples linking the same two entities).
- Both directions added: `(A, B)` and `(B, A)` get the same weight.
- Within a triple, only the subject-object pair gets an edge (the predicate is dropped before edge creation: `triple = np.array(triple)[[0, 2]]`).

### Synonymy edges (E→)

Computed in three phases:

**Phase 1: Encode every entity.**
- Default model: `facebook/contriever`.
- Mean-pooled token embeddings.
- L2-normalised to unit length.

**Phase 2: Precompute nearest neighbours.**
- FAISS `IndexFlat` with `METRIC_INNER_PRODUCT`.
- Inner product on L2-normalised vectors = cosine similarity.
- Save top-2047 neighbours per entity to disk.

**Phase 3: Filter into edges.**

```python
for phrase in kb_similarity.keys():
    if len(re.sub('[^A-Za-z0-9]', '', phrase)) > 2:        # skip short phrases
        for nn, score in kb_similarity[phrase]:
            if score < threshold or num_nns > 100:          # threshold 0.8, cap 100
                break
            if nn != phrase and nn in kb_phrase_dict:
                graph_plus[(phrase_id, phrase2_id)] = similarity_max * score  # weight = cosine
```

Filters:
1. Entity name must have > 2 alphanumeric chars.
2. Cosine ≥ threshold (default 0.8).
3. Max 100 synonyms per entity.
4. No self-loops.
5. Both entities must exist in the KG.

**Edge weight = raw cosine similarity** (since `similarity_max = 1.0`), so in `[0.8, 1.0]`.

### The combined graph: `graph_plus`

Both edge types live in one dictionary, keyed by `(node_i, node_j)`. They are added directly into the same map — not normalised separately and merged.

**Implementation quirk worth flagging:** the synonymy step uses assignment, not addition:
```python
graph_plus[sim_edge] = similarity_max * score   # = , not +=
```
If a pair `(A, B)` has both a triple edge (weight 5, say) and a synonymy edge (cosine 0.9), the synonymy assignment **overwrites** the triple weight. In practice this rarely happens (entities linked by triples usually aren't also high-cosine synonyms), but it is a real implementation detail.

**Unit mismatch:** triple weights are counts (1.0, 2.0, ...); synonymy weights are similarities (0.8–1.0). They live in the same dictionary on incomparable scales. Per-node normalization at PageRank time partially smooths this out, but a high-cooccurrence node will route most of its random-walk probability via triple edges.

### Personalized PageRank (PPR)

**Plain PageRank** ranks nodes by importance via a random walk that follows edges with probability `1-α` and teleports to a uniform-random node with probability `α`. Stationary distribution = PageRank.

**Personalized PageRank** changes one thing: the teleport step goes to a *specific set of seed nodes* (the personalisation vector `s`) instead of uniformly. This biases the walk toward neighbourhoods of those seeds.

The fixed-point equation:
```
r = (1 - α) · M · r  +  α · s
```

- `r` — PageRank vector (probability per node).
- `M` — transition matrix (`M[i,j]` = probability of going from `j` to `i`; weighted edges normalised per node).
- `α` — teleport probability (default 0.15, paper uses 0.1).
- `s` — personalisation vector (uniform over query nodes; zero elsewhere).

The equation says: in equilibrium, the probability of being at any node equals the probability of arriving there, which can happen via *walking* `(1-α)·M·r` or *teleporting* `α·s`.

Solved by **power iteration**: start with `r₀`, repeat `r_{t+1} = (1-α)·M·r_t + α·s` until convergence (~20–50 iterations).

In HippoRAG: igraph's `personalized_pagerank` does this in optimised C. Per-query cost is tens of milliseconds.

### Node specificity

An IDF-like weighting applied to node scores before passage ranking.

**Motivation**: common entities (appearing in many passages) would otherwise dominate passage scores. Specific entities (appearing in few passages) carry more discriminative signal.

**Formula**: `specificity(i) = 1 / (count of passages containing entity i)`.

A node appearing in 1 passage has specificity 1.0; a node appearing in 500 passages has specificity 0.002.

**Used as**: `n_weighted[i] = ppr_score[i] × specificity(i)`. Then `p = n_weighted · P`.

Without this, queries containing both rare and common entities would have results dominated by the common entities (e.g., "Alice" should dominate "lunch" in the query "What did Alice eat for lunch?").

### From node scores to passage scores

The `P` matrix is `nodes × passages` where `P[i, j]` indicates how strongly node `i` is associated with passage `j` (essentially counting occurrences).

Final passage scoring:
```
p = (PPR_scores × node_specificity) · P
```

`p[j]` is the relevance score for passage `j`. Top-K by `p` is returned.

---

## L2 normalization (background)

Used throughout HippoRAG's embedding work. The L2 norm of a vector is its Euclidean length:

```
||v||₂ = sqrt(v₁² + v₂² + ... + vₙ²)
```

L2 normalization is dividing by this length:

```
v_normalized = v / ||v||₂
```

The resulting vector has length 1 (lies on the unit sphere); direction preserved.

**Why it matters for cosine similarity:**
```
cosine_similarity(a, b) = (a · b) / (||a|| · ||b||)
```

If `a` and `b` are L2-normalised, `||a||·||b|| = 1`, so cosine similarity collapses to plain dot product. This is why HippoRAG uses `faiss.normalize_L2` + `METRIC_INNER_PRODUCT` — it gets cosine similarity at inner-product speed.

---

## Cost economics

| System | Indexing cost | Per-query LLM cost | Best when |
|---|---|---|---|
| **Vanilla dense RAG** | Low (embeddings only) | Zero (no LLM per query) | Single-hop questions, cost-sensitive |
| **HippoRAG** | High (OpenIE per passage) | One small LLM call (NER) | Many queries on the same corpus; multi-hop |
| **IRCoT (iterative)** | Low | Many LLM calls per query | Rare, when you don't index ahead |

HippoRAG's advantage compounds with query volume. With 1,000 queries on a 5,000-passage corpus, HippoRAG's amortised cost beats IRCoT clearly. With a single query, vanilla dense RAG is cheapest.

---

## Key design choices and their implications

1. **Predicates discarded.** Robust to OpenIE label errors but loses relation semantics. The graph cannot distinguish "studies under" from "fired."
2. **Two incompatible weight units in one dictionary.** Triple counts (integer) and synonymy cosines (0.8–1.0) coexist. Not normalised to comparable scales.
3. **Synonymy edge weight = raw cosine.** No transformation; if cosine is 0.85, weight is 0.85.
4. **Synonymy step overwrites triple weights for shared pairs.** Implementation quirk; rarely visible in practice.
5. **Entire synonymy structure depends on the embedding model.** Different retrievers produce different graphs and different downstream performance.
6. **Static index — no incremental updates.** Adding a new passage requires recomputing OpenIE, re-encoding entities, and reconstructing the synonymy edges (since new entities affect everyone's nearest-neighbour lists).
7. **No temporal awareness.** Fact changes ("user moved to Berlin" after "user lives in Paris") are not handled — both facts remain in the graph with equal weight.

---

## Things to remember for the reproduction

- **Indexing is the expensive part.** Budget ~$50–$200 for a moderate-sized corpus on GPT-3.5; more for GPT-4.
- **Cache the index.** Don't rebuild between experiments.
- **Embedding model choice matters more than the paper emphasises.** Pick one and stick with it through the reproduction.
- **Hyperparameters that quietly matter:**
  - `sim_threshold` (synonymy cosine cutoff; default 0.8)
  - `damping` factor in PPR (default 0.1 in HippoRAG, sometimes called α elsewhere)
  - max neighbours per entity (cap 100 in the code)
  - `node_specificity` flag (whether to apply IDF-like weighting)
- **PPR is fast.** Optimise the LLM calls, not the graph computation.
- **Use the LEGACY branch** of the OSU-NLP-Group/HippoRAG repo for the original paper. The `main` and `develop` branches are HippoRAG 2.

---

## Connections to broader research themes

- **Static embedding bottleneck.** HippoRAG's synonymy edges are frozen at index time. If the embedding model is updated, the entire graph has to be rebuilt. This connects to the same problem flagged in A-Mem and Chain-of-Memory.
- **No reconsolidation.** HippoRAG does not update memories on retrieval. The graph is set at indexing time and never changes from queries.
- **No active forgetting.** No mechanism to prune stale or contradicted memories. Capacity grows monotonically with new content.
- **The brain analogy is loose.** Real hippocampal memory does reconsolidate on recall, does actively forget, does integrate over time. HippoRAG borrows the indexing motif but not these dynamic properties — which is exactly the gap your downstream research could address.

---

## Open questions (for your future research)

1. How performance-sensitive is HippoRAG to the embedding model choice? The paper does some ablation but not exhaustive.
2. What happens if you swap PPR for a learned graph neural network at retrieval?
3. Can you add reconsolidation-style updates to the KG without rebuilding the whole thing?
4. Can synonymy edges be made *adaptive* — strengthening or weakening over time based on retrieval feedback?
5. What's the right way to handle a fact change (e.g., user moved cities)? Does the graph need explicit versioning?
6. How does HippoRAG perform on benchmarks designed for *agent memory* (MemoryAgentBench, LongMemEval) rather than the multi-hop QA benchmarks the paper tests on?
