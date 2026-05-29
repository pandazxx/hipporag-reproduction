# Trace — q13  [implicit_conceptual, expect=A-Mem]

**Question:** What hobbies has Sam been less active in lately?

**Expected answer:** Spanish learning (slipped to once a week) and climbing (first session in two weeks before m38)

**Required facts:** ['m37', 'm38']

## Step 1 — query→triple top-K (cosine on triple-text embeddings)

| Cosine | Subject | Predicate | Object |
|---|---|---|---|
| 0.522 | `Sam` | has been doing | `rock climbing` |
| 0.448 | `Sam` | went climbing at | `Berkeley Ironworks` |
| 0.431 | `Sam` | started learning Spanish | `two months ago` |
| 0.424 | `Sam` | has goal | `discover new outdoor climbing destinations` |
| 0.414 | `Sam` | has favorite climbing problems | `V4-V5 boulder routes` |
| 0.413 | `Sam` | goes rock climbing at | `Berkeley Ironworks` |
| 0.408 | `Sam` | uses | `Duolingo` |
| 0.401 | `Sam` | started | `side project` |
| 0.400 | `Sam` | feeling | `burned out` |
| 0.398 | `Sam` | gave notice at | `TechCorp` |

## Step 2 — recognition memory (LLM filter)

| Subject | Predicate | Object |
|---|---|---|
| `Sam` | started learning Spanish | `two months ago` |
| `Sam` | started | `side project` |
| `Sam` | feeling | `burned out` |

## Step 3 — top 5 retrieved passages

| Rank | Memory | PPR | Hit | Text |
|---|---|---|---|---|
| 1 | `m23` | 0.00299 |  | Sam is feeling burned out at TechCorp due to long hours and … |
| 2 | `m16` | 0.00284 |  | Sam started a side project: building a web scraper to find n… |
| 3 | `m34` | 0.00268 |  | Sam booked flights to Boston for May 13 through 17 to be the… |
| 4 | `m06` | 0.00263 |  | Sam started learning Spanish two months ago, mainly for an u… |
| 5 | `m37` | 0.00252 | ✓ | Sam's Spanish practice has slipped to once a week since star… |

## Search subgraph

Seeds from filtered triples (red), top-PPR phrases (blue), top-5 passage nodes (green if required, grey otherwise).

```mermaid
graph LR
    n25(["Sam"]):::seed
    n66(["two months ago"]):::seed
    n39(["burned out"]):::seed
    n63(["side project"]):::seed
    n32["StartupCo"]:::phrase
    n56["other companies"]:::phrase
    n30["Spanish"]:::phrase
    n0["Alex"]:::phrase
    n61["scraper"]:::phrase
    n11["March"]:::phrase
    n4["Boston"]:::phrase
    n1["Amazon"]:::phrase
    n53["long hours"]:::phrase
    n7["Duolingo"]:::phrase
    g91["m23: Sam is feeling burned out at TechCo…"]:::passage
    g84["m16: Sam started a side project: buildin…"]:::passage
    g102["m34: Sam booked flights to Boston for Ma…"]:::passage
    g74["m06: Sam started learning Spanish two mo…"]:::passage
    g105["m37: Sam's Spanish practice has slipped …"]:::hit
    n25 --- n66
    n25 --- n39
    n25 --- n63
    n25 --- n32
    n25 --- n56
    n25 --- n30
    n25 --- n61
    n25 --- n53
    n39 --- n66
    n39 --- n63
    n39 --- n56
    n39 --- n61
    n39 --- n53
    n63 --- n66
    n32 --- n66
    n32 --- n39
    n32 --- n63
    n32 --- n56
    n32 --- n61
    n32 --- n53
    n56 --- n66
    n56 --- n63
    n56 --- n61
    n30 --- n66
    n30 --- n39
    n30 --- n63
    n30 --- n32
    n30 --- n56
    n30 --- n61
    n30 --- n53
    n0 --- n25
    n0 --- n66
    n0 --- n39
    n0 --- n63
    n0 --- n32
    n0 --- n56
    n0 --- n30
    n0 --- n61
    n0 --- n11
    n0 --- n4
    n0 --- n1
    n0 --- n53
    n0 --- n7
    n61 --- n66
    n61 --- n63
    n11 --- n25
    n11 --- n66
    n11 --- n39
    n11 --- n63
    n11 --- n32
    n11 --- n56
    n11 --- n30
    n11 --- n61
    n11 --- n53
    n4 --- n25
    n4 --- n66
    n4 --- n39
    n4 --- n63
    n4 --- n32
    n4 --- n56
    n4 --- n30
    n4 --- n61
    n4 --- n11
    n4 --- n53
    n4 --- n7
    n1 --- n25
    n1 --- n66
    n1 --- n39
    n1 --- n63
    n1 --- n32
    n1 --- n56
    n1 --- n30
    n1 --- n61
    n1 --- n11
    n1 --- n4
    n1 --- n53
    n1 --- n7
    n53 --- n66
    n53 --- n63
    n53 --- n56
    n53 --- n61
    n7 --- n25
    n7 --- n66
    n7 --- n39
    n7 --- n63
    n7 --- n32
    n7 --- n56
    n7 --- n30
    n7 --- n61
    n7 --- n11
    n7 --- n53
    n25 -.-> g102
    n25 -.-> g105
    n25 -.-> g74
    n25 -.-> g84
    n25 -.-> g91
    n66 -.-> g74
    n39 -.-> g91
    n63 -.-> g84
    n32 -.-> g105
    n30 -.-> g105
    n30 -.-> g74
    n4 -.-> g102
    n53 -.-> g91
    classDef seed fill:#fdd,stroke:#c44,stroke-width:2px
    classDef phrase fill:#eef,stroke:#446
    classDef passage fill:#f5f5f5,stroke:#666
    classDef hit fill:#dfd,stroke:#080,stroke-width:3px
```
