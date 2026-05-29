# Trace — q21  [absence_abstention, expect=tie]

**Question:** Does Sam have any pets?

**Expected answer:** unknown / not mentioned

**Required facts:** (none — absence/abstention)

## Step 1 — query→triple top-K (cosine on triple-text embeddings)

| Cosine | Subject | Predicate | Object |
|---|---|---|---|
| 0.441 | `Sam` | uses | `Duolingo` |
| 0.440 | `Sam` | has partner | `Alex` |
| 0.439 | `Sam` | practices | `Spanish` |
| 0.439 | `Sam` | practices | `Spanish` |
| 0.427 | `Sam` | has been doing | `rock climbing` |
| 0.424 | `Sam` | lives in | `Oakland` |
| 0.421 | `Sam` | has manager | `Jennifer` |
| 0.415 | `Sam` | has mother | `Maria` |
| 0.411 | `Sam` | went climbing at | `Berkeley Ironworks` |
| 0.407 | `Sam` | climbed at | `Yosemite` |

## Step 2 — recognition memory (LLM filter)

_(LLM kept no triples)_

## Step 3 — top 5 retrieved passages

| Rank | Memory | PPR | Hit | Text |
|---|---|---|---|---|
| 1 | `m08` | 0.00763 |  | Sam goes rock climbing at Berkeley Ironworks gym. |
| 2 | `m38` | 0.00697 |  | Sam went climbing at Berkeley Ironworks this morning, first … |
| 3 | `m40` | 0.00623 |  | Sam is planning a long climbing trip to Joshua Tree in late … |
| 4 | `m07` | 0.00622 |  | Sam uses Duolingo daily for Spanish practice. |
| 5 | `m15` | 0.00619 |  | Sam plans to visit Maria for her birthday in mid-May. |

## Search subgraph

Seeds from filtered triples (red), top-PPR phrases (blue), top-5 passage nodes (green if required, grey otherwise).

```mermaid
graph LR
    n25["Sam"]:::phrase
    n32["StartupCo"]:::phrase
    n0["Alex"]:::phrase
    n4["Boston"]:::phrase
    n30["Spanish"]:::phrase
    n13["Maria"]:::phrase
    n11["March"]:::phrase
    n61["scraper"]:::phrase
    n33["TechCorp"]:::phrase
    n56["other companies"]:::phrase
    g76["m08: Sam goes rock climbing at Berkeley …"]:::passage
    g106["m38: Sam went climbing at Berkeley Ironw…"]:::passage
    g108["m40: Sam is planning a long climbing tri…"]:::passage
    g75["m07: Sam uses Duolingo daily for Spanish…"]:::passage
    g83["m15: Sam plans to visit Maria for her bi…"]:::passage
    n25 --- n32
    n25 --- n30
    n25 --- n61
    n25 --- n33
    n25 --- n56
    n32 --- n61
    n32 --- n33
    n32 --- n56
    n0 --- n25
    n0 --- n32
    n0 --- n4
    n0 --- n30
    n0 --- n13
    n0 --- n11
    n0 --- n61
    n0 --- n33
    n0 --- n56
    n4 --- n25
    n4 --- n32
    n4 --- n30
    n4 --- n13
    n4 --- n11
    n4 --- n61
    n4 --- n33
    n4 --- n56
    n30 --- n32
    n30 --- n61
    n30 --- n33
    n30 --- n56
    n13 --- n25
    n13 --- n32
    n13 --- n30
    n13 --- n61
    n13 --- n33
    n13 --- n56
    n11 --- n25
    n11 --- n32
    n11 --- n30
    n11 --- n13
    n11 --- n61
    n11 --- n33
    n11 --- n56
    n33 --- n61
    n33 --- n56
    n56 --- n61
    n25 -.-> g106
    n25 -.-> g75
    n25 -.-> g108
    n25 -.-> g76
    n25 -.-> g83
    n0 -.-> g108
    n30 -.-> g75
    n13 -.-> g83
    n11 -.-> g108
    classDef seed fill:#fdd,stroke:#c44,stroke-width:2px
    classDef phrase fill:#eef,stroke:#446
    classDef passage fill:#f5f5f5,stroke:#666
    classDef hit fill:#dfd,stroke:#080,stroke-width:3px
```
