# Trace — q04  [single_hop, expect=tie]

**Question:** What climbing shoes did Sam order?

**Expected answer:** La Sportiva Solution

**Required facts:** ['m39']

## Step 1 — query→triple top-K (cosine on triple-text embeddings)

| Cosine | Subject | Predicate | Object |
|---|---|---|---|
| 0.551 | `Sam` | went climbing at | `Berkeley Ironworks` |
| 0.530 | `Sam` | climbed at | `Yosemite` |
| 0.509 | `Sam` | ordered | `La Sportiva Solution` |
| 0.504 | `Sam` | has favorite climbing problems | `V4-V5 boulder routes` |
| 0.500 | `Sam` | climbed with | `Alex` |
| 0.494 | `Sam` | goes rock climbing at | `Berkeley Ironworks` |
| 0.470 | `Sam` | has been doing | `rock climbing` |
| 0.466 | `Sam` | has goal | `discover new outdoor climbing destinations` |
| 0.413 | `Sam` | decided to rewrite | `climbing scraper` |
| 0.394 | `Sam` | booked flights to | `Boston` |

## Step 2 — recognition memory (LLM filter)

| Subject | Predicate | Object |
|---|---|---|
| `Sam` | ordered | `La Sportiva Solution` |

## Step 3 — top 5 retrieved passages

| Rank | Memory | PPR | Hit | Text |
|---|---|---|---|---|
| 1 | `m39` | 0.00553 | ✓ | Sam ordered a new pair of climbing shoes — the La Sportiva S… |
| 2 | `m08` | 0.00339 |  | Sam goes rock climbing at Berkeley Ironworks gym. |
| 3 | `m34` | 0.00334 |  | Sam booked flights to Boston for May 13 through 17 to be the… |
| 4 | `m38` | 0.00332 |  | Sam went climbing at Berkeley Ironworks this morning, first … |
| 5 | `m16` | 0.00315 |  | Sam started a side project: building a web scraper to find n… |

## Search subgraph

Seeds from filtered triples (red), top-PPR phrases (blue), top-5 passage nodes (green if required, grey otherwise).

```mermaid
graph LR
    n25(["Sam"]):::seed
    n10(["La Sportiva Solution"]):::seed
    n32["StartupCo"]:::phrase
    n11["March"]:::phrase
    n0["Alex"]:::phrase
    n30["Spanish"]:::phrase
    n63["side project"]:::phrase
    n56["other companies"]:::phrase
    n61["scraper"]:::phrase
    n4["Boston"]:::phrase
    n1["Amazon"]:::phrase
    n7["Duolingo"]:::phrase
    g107["m39: Sam ordered a new pair of climbing …"]:::hit
    g76["m08: Sam goes rock climbing at Berkeley …"]:::passage
    g102["m34: Sam booked flights to Boston for Ma…"]:::passage
    g106["m38: Sam went climbing at Berkeley Ironw…"]:::passage
    g84["m16: Sam started a side project: buildin…"]:::passage
    n25 --- n32
    n25 --- n30
    n25 --- n63
    n25 --- n56
    n25 --- n61
    n10 --- n25
    n10 --- n32
    n10 --- n11
    n10 --- n30
    n10 --- n63
    n10 --- n56
    n10 --- n61
    n32 --- n63
    n32 --- n56
    n32 --- n61
    n11 --- n25
    n11 --- n32
    n11 --- n30
    n11 --- n63
    n11 --- n56
    n11 --- n61
    n0 --- n25
    n0 --- n10
    n0 --- n32
    n0 --- n11
    n0 --- n30
    n0 --- n63
    n0 --- n56
    n0 --- n61
    n0 --- n4
    n0 --- n1
    n0 --- n7
    n30 --- n32
    n30 --- n63
    n30 --- n56
    n30 --- n61
    n56 --- n63
    n56 --- n61
    n61 --- n63
    n4 --- n25
    n4 --- n10
    n4 --- n32
    n4 --- n11
    n4 --- n30
    n4 --- n63
    n4 --- n56
    n4 --- n61
    n4 --- n7
    n1 --- n25
    n1 --- n10
    n1 --- n32
    n1 --- n11
    n1 --- n30
    n1 --- n63
    n1 --- n56
    n1 --- n61
    n1 --- n4
    n1 --- n7
    n7 --- n25
    n7 --- n10
    n7 --- n32
    n7 --- n11
    n7 --- n30
    n7 --- n63
    n7 --- n56
    n7 --- n61
    n25 -.-> g102
    n25 -.-> g106
    n25 -.-> g107
    n25 -.-> g76
    n25 -.-> g84
    n10 -.-> g107
    n11 -.-> g107
    n63 -.-> g84
    n4 -.-> g102
    classDef seed fill:#fdd,stroke:#c44,stroke-width:2px
    classDef phrase fill:#eef,stroke:#446
    classDef passage fill:#f5f5f5,stroke:#666
    classDef hit fill:#dfd,stroke:#080,stroke-width:3px
```
