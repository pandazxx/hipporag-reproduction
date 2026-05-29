# Trace — q09  [deep_multi_hop, expect=HippoRAG]

**Question:** What is the profession of the partner of the engineer who has a brother in Seattle?

**Expected answer:** graphic designer

**Required facts:** ['m05', 'm13']

## Step 1 — query→triple top-K (cosine on triple-text embeddings)

| Cosine | Subject | Predicate | Object |
|---|---|---|---|
| 0.386 | `Amazon` | has headquarters at | `Seattle` |
| 0.378 | `David` | has office at | `Seattle` |
| 0.352 | `Sam` | has partner | `Alex` |
| 0.347 | `Sam` | is | `software engineer` |
| 0.330 | `Sam` | works at | `TechCorp` |
| 0.330 | `Sam` | works at | `TechCorp` |
| 0.330 | `Sam` | works at | `TechCorp` |
| 0.327 | `David` | lives in | `Seattle` |
| 0.326 | `David` | works at | `Amazon` |
| 0.323 | `David` | is brother of | `Sam` |

## Step 2 — recognition memory (LLM filter)

| Subject | Predicate | Object |
|---|---|---|
| `Sam` | has partner | `Alex` |
| `Sam` | is | `software engineer` |
| `David` | is brother of | `Sam` |
| `David` | lives in | `Seattle` |

## Step 3 — top 5 retrieved passages

| Rank | Memory | PPR | Hit | Text |
|---|---|---|---|---|
| 1 | `m13` | 0.00276 | ✓ | Sam's brother David lives in Seattle. |
| 2 | `m34` | 0.00240 |  | Sam booked flights to Boston for May 13 through 17 to be the… |
| 3 | `m22` | 0.00217 |  | Sam climbed with Alex at Yosemite. Alex is also a climber bu… |
| 4 | `m40` | 0.00217 |  | Sam is planning a long climbing trip to Joshua Tree in late … |
| 5 | `m14` | 0.00213 |  | David works at Amazon as a product manager. His office is at… |

## Search subgraph

Seeds from filtered triples (red), top-PPR phrases (blue), top-5 passage nodes (green if required, grey otherwise).

```mermaid
graph LR
    n0(["Alex"]):::seed
    n64(["software engineer"]):::seed
    n6(["David"]):::seed
    n25(["Sam"]):::seed
    n29(["Seattle"]):::seed
    n63["side project"]:::phrase
    n4["Boston"]:::phrase
    n30["Spanish"]:::phrase
    n56["other companies"]:::phrase
    n1["Amazon"]:::phrase
    n32["StartupCo"]:::phrase
    n61["scraper"]:::phrase
    n11["March"]:::phrase
    n39["burned out"]:::phrase
    n7["Duolingo"]:::phrase
    g81["m13: Sam's brother David lives in Seattl…"]:::hit
    g102["m34: Sam booked flights to Boston for Ma…"]:::passage
    g90["m22: Sam climbed with Alex at Yosemite. …"]:::passage
    g108["m40: Sam is planning a long climbing tri…"]:::passage
    g82["m14: David works at Amazon as a product …"]:::passage
    n0 --- n64
    n0 --- n6
    n0 --- n25
    n0 --- n29
    n0 --- n63
    n0 --- n4
    n0 --- n30
    n0 --- n56
    n0 --- n1
    n0 --- n32
    n0 --- n61
    n0 --- n11
    n0 --- n39
    n0 --- n7
    n6 --- n64
    n6 --- n25
    n6 --- n29
    n6 --- n63
    n6 --- n30
    n6 --- n56
    n6 --- n32
    n6 --- n61
    n6 --- n11
    n6 --- n39
    n6 --- n7
    n25 --- n64
    n25 --- n29
    n25 --- n63
    n25 --- n30
    n25 --- n56
    n25 --- n32
    n25 --- n61
    n25 --- n39
    n29 --- n64
    n29 --- n63
    n29 --- n30
    n29 --- n56
    n29 --- n32
    n29 --- n61
    n29 --- n39
    n63 --- n64
    n4 --- n64
    n4 --- n6
    n4 --- n25
    n4 --- n29
    n4 --- n63
    n4 --- n30
    n4 --- n56
    n4 --- n32
    n4 --- n61
    n4 --- n11
    n4 --- n39
    n4 --- n7
    n30 --- n64
    n30 --- n63
    n30 --- n56
    n30 --- n32
    n30 --- n61
    n30 --- n39
    n56 --- n64
    n56 --- n63
    n56 --- n61
    n1 --- n64
    n1 --- n6
    n1 --- n25
    n1 --- n29
    n1 --- n63
    n1 --- n4
    n1 --- n30
    n1 --- n56
    n1 --- n32
    n1 --- n61
    n1 --- n11
    n1 --- n39
    n1 --- n7
    n32 --- n64
    n32 --- n63
    n32 --- n56
    n32 --- n61
    n32 --- n39
    n61 --- n64
    n61 --- n63
    n11 --- n64
    n11 --- n25
    n11 --- n29
    n11 --- n63
    n11 --- n30
    n11 --- n56
    n11 --- n32
    n11 --- n61
    n11 --- n39
    n39 --- n64
    n39 --- n63
    n39 --- n56
    n39 --- n61
    n7 --- n64
    n7 --- n25
    n7 --- n29
    n7 --- n63
    n7 --- n30
    n7 --- n56
    n7 --- n32
    n7 --- n61
    n7 --- n11
    n7 --- n39
    n0 -.-> g108
    n0 -.-> g90
    n6 -.-> g81
    n6 -.-> g82
    n25 -.-> g102
    n25 -.-> g108
    n25 -.-> g81
    n25 -.-> g90
    n29 -.-> g81
    n29 -.-> g82
    n4 -.-> g102
    n1 -.-> g82
    n11 -.-> g108
    classDef seed fill:#fdd,stroke:#c44,stroke-width:2px
    classDef phrase fill:#eef,stroke:#446
    classDef passage fill:#f5f5f5,stroke:#666
    classDef hit fill:#dfd,stroke:#080,stroke-width:3px
```
