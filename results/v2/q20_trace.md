# Trace — q20  [absence_abstention, expect=tie]

**Question:** What is Sam's favorite food?

**Expected answer:** unknown / not mentioned

**Required facts:** (none — absence/abstention)

## Step 1 — query→triple top-K (cosine on triple-text embeddings)

| Cosine | Subject | Predicate | Object |
|---|---|---|---|
| 0.429 | `Sam` | has favorite climbing problems | `V4-V5 boulder routes` |
| 0.414 | `Sam` | practices | `Spanish` |
| 0.414 | `Sam` | practices | `Spanish` |
| 0.414 | `Sam` | uses | `Duolingo` |
| 0.403 | `Sam` | climbed at | `Yosemite` |
| 0.400 | `Sam` | goes rock climbing at | `Berkeley Ironworks` |
| 0.398 | `Sam` | is learning | `Spanish` |
| 0.396 | `Sam` | went climbing at | `Berkeley Ironworks` |
| 0.387 | `Yosemite` | was visited by | `Sam` |
| 0.385 | `Sam` | started learning Spanish | `two months ago` |

## Step 2 — recognition memory (LLM filter)

_(LLM kept no triples)_

## Step 3 — top 5 retrieved passages

| Rank | Memory | PPR | Hit | Text |
|---|---|---|---|---|
| 1 | `m08` | 0.00759 |  | Sam goes rock climbing at Berkeley Ironworks gym. |
| 2 | `m10` | 0.00691 |  | Sam's favorite climbing problems are V4-V5 boulder routes. |
| 3 | `m38` | 0.00666 |  | Sam went climbing at Berkeley Ironworks this morning, first … |
| 4 | `m15` | 0.00627 |  | Sam plans to visit Maria for her birthday in mid-May. |
| 5 | `m34` | 0.00624 |  | Sam booked flights to Boston for May 13 through 17 to be the… |

## Search subgraph

Seeds from filtered triples (red), top-PPR phrases (blue), top-5 passage nodes (green if required, grey otherwise).

```mermaid
graph LR
    n25["Sam"]:::phrase
    n32["StartupCo"]:::phrase
    n0["Alex"]:::phrase
    n4["Boston"]:::phrase
    n30["Spanish"]:::phrase
    n61["scraper"]:::phrase
    n13["Maria"]:::phrase
    n11["March"]:::phrase
    n56["other companies"]:::phrase
    n63["side project"]:::phrase
    g76["m08: Sam goes rock climbing at Berkeley …"]:::passage
    g78["m10: Sam's favorite climbing problems ar…"]:::passage
    g106["m38: Sam went climbing at Berkeley Ironw…"]:::passage
    g83["m15: Sam plans to visit Maria for her bi…"]:::passage
    g102["m34: Sam booked flights to Boston for Ma…"]:::passage
    n25 --- n32
    n25 --- n30
    n25 --- n61
    n25 --- n56
    n25 --- n63
    n32 --- n61
    n32 --- n56
    n32 --- n63
    n0 --- n25
    n0 --- n32
    n0 --- n4
    n0 --- n30
    n0 --- n61
    n0 --- n13
    n0 --- n11
    n0 --- n56
    n0 --- n63
    n4 --- n25
    n4 --- n32
    n4 --- n30
    n4 --- n61
    n4 --- n13
    n4 --- n11
    n4 --- n56
    n4 --- n63
    n30 --- n32
    n30 --- n61
    n30 --- n56
    n30 --- n63
    n61 --- n63
    n13 --- n25
    n13 --- n32
    n13 --- n30
    n13 --- n61
    n13 --- n56
    n13 --- n63
    n11 --- n25
    n11 --- n32
    n11 --- n30
    n11 --- n61
    n11 --- n13
    n11 --- n56
    n11 --- n63
    n56 --- n61
    n56 --- n63
    n25 -.-> g102
    n25 -.-> g106
    n25 -.-> g76
    n25 -.-> g78
    n25 -.-> g83
    n4 -.-> g102
    n13 -.-> g83
    classDef seed fill:#fdd,stroke:#c44,stroke-width:2px
    classDef phrase fill:#eef,stroke:#446
    classDef passage fill:#f5f5f5,stroke:#666
    classDef hit fill:#dfd,stroke:#080,stroke-width:3px
```
