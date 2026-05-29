# Trace — q01  [single_hop, expect=tie]

**Question:** Where does Sam live?

**Expected answer:** Oakland, California

**Required facts:** ['m04']

## Step 1 — query→triple top-K (cosine on triple-text embeddings)

| Cosine | Subject | Predicate | Object |
|---|---|---|---|
| 0.544 | `Sam` | lives in | `Oakland` |
| 0.539 | `Sam` | lives in | `California` |
| 0.460 | `Sam` | works at | `TechCorp` |
| 0.460 | `Sam` | works at | `TechCorp` |
| 0.460 | `Sam` | works at | `TechCorp` |
| 0.457 | `Sam` | works at | `StartupCo` |
| 0.457 | `Sam` | works at | `StartupCo` |
| 0.455 | `Sam` | has partner | `Alex` |
| 0.447 | `Sam` | went climbing at | `Berkeley Ironworks` |
| 0.446 | `Sam` | uses | `Duolingo` |

## Step 2 — recognition memory (LLM filter)

| Subject | Predicate | Object |
|---|---|---|
| `Sam` | lives in | `Oakland` |
| `Sam` | lives in | `California` |

## Step 3 — top 5 retrieved passages

| Rank | Memory | PPR | Hit | Text |
|---|---|---|---|---|
| 1 | `m04` | 0.00384 | ✓ | Sam lives in Oakland, California. |
| 2 | `m34` | 0.00283 |  | Sam booked flights to Boston for May 13 through 17 to be the… |
| 3 | `m23` | 0.00259 |  | Sam is feeling burned out at TechCorp due to long hours and … |
| 4 | `m37` | 0.00256 |  | Sam's Spanish practice has slipped to once a week since star… |
| 5 | `m08` | 0.00254 |  | Sam goes rock climbing at Berkeley Ironworks gym. |

## Search subgraph

Seeds from filtered triples (red), top-PPR phrases (blue), top-5 passage nodes (green if required, grey otherwise).

```mermaid
graph LR
    n25(["Sam"]):::seed
    n5(["California"]):::seed
    n21(["Oakland"]):::seed
    n32["StartupCo"]:::phrase
    n0["Alex"]:::phrase
    n30["Spanish"]:::phrase
    n63["side project"]:::phrase
    n56["other companies"]:::phrase
    n4["Boston"]:::phrase
    n61["scraper"]:::phrase
    n11["March"]:::phrase
    n1["Amazon"]:::phrase
    n39["burned out"]:::phrase
    g72["m04: Sam lives in Oakland, California."]:::hit
    g102["m34: Sam booked flights to Boston for Ma…"]:::passage
    g91["m23: Sam is feeling burned out at TechCo…"]:::passage
    g105["m37: Sam's Spanish practice has slipped …"]:::passage
    g76["m08: Sam goes rock climbing at Berkeley …"]:::passage
    n25 --- n32
    n25 --- n30
    n25 --- n63
    n25 --- n56
    n25 --- n61
    n25 --- n39
    n5 --- n25
    n5 --- n21
    n5 --- n32
    n5 --- n30
    n5 --- n63
    n5 --- n56
    n5 --- n61
    n5 --- n11
    n5 --- n39
    n21 --- n25
    n21 --- n32
    n21 --- n30
    n21 --- n63
    n21 --- n56
    n21 --- n61
    n21 --- n39
    n32 --- n63
    n32 --- n56
    n32 --- n61
    n32 --- n39
    n0 --- n25
    n0 --- n5
    n0 --- n21
    n0 --- n32
    n0 --- n30
    n0 --- n63
    n0 --- n56
    n0 --- n4
    n0 --- n61
    n0 --- n11
    n0 --- n1
    n0 --- n39
    n30 --- n32
    n30 --- n63
    n30 --- n56
    n30 --- n61
    n30 --- n39
    n56 --- n63
    n56 --- n61
    n4 --- n25
    n4 --- n5
    n4 --- n21
    n4 --- n32
    n4 --- n30
    n4 --- n63
    n4 --- n56
    n4 --- n61
    n4 --- n11
    n4 --- n39
    n61 --- n63
    n11 --- n25
    n11 --- n21
    n11 --- n32
    n11 --- n30
    n11 --- n63
    n11 --- n56
    n11 --- n61
    n11 --- n39
    n1 --- n25
    n1 --- n5
    n1 --- n21
    n1 --- n32
    n1 --- n30
    n1 --- n63
    n1 --- n56
    n1 --- n4
    n1 --- n61
    n1 --- n11
    n1 --- n39
    n39 --- n63
    n39 --- n56
    n39 --- n61
    n25 -.-> g102
    n25 -.-> g72
    n25 -.-> g105
    n25 -.-> g76
    n25 -.-> g91
    n5 -.-> g72
    n21 -.-> g72
    n32 -.-> g105
    n30 -.-> g105
    n4 -.-> g102
    n39 -.-> g91
    classDef seed fill:#fdd,stroke:#c44,stroke-width:2px
    classDef phrase fill:#eef,stroke:#446
    classDef passage fill:#f5f5f5,stroke:#666
    classDef hit fill:#dfd,stroke:#080,stroke-width:3px
```
