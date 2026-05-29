# Trace — q05  [two_hop, expect=tie]

**Question:** In which city is the company that David works for headquartered?

**Expected answer:** Seattle

**Required facts:** ['m14']

## Step 1 — query→triple top-K (cosine on triple-text embeddings)

| Cosine | Subject | Predicate | Object |
|---|---|---|---|
| 0.496 | `David` | has office at | `Seattle` |
| 0.472 | `David` | works at | `Amazon` |
| 0.439 | `David` | lives in | `Seattle` |
| 0.348 | `David` | will attend | `Maria's birthday` |
| 0.339 | `David` | will fly to | `Boston` |
| 0.332 | `Sam` | works at | `TechCorp` |
| 0.332 | `Sam` | works at | `TechCorp` |
| 0.332 | `Sam` | works at | `TechCorp` |
| 0.331 | `Sam` | works at | `StartupCo` |
| 0.331 | `Sam` | works at | `StartupCo` |

## Step 2 — recognition memory (LLM filter)

| Subject | Predicate | Object |
|---|---|---|
| `David` | works at | `Amazon` |
| `David` | has office at | `Seattle` |

## Step 3 — top 5 retrieved passages

| Rank | Memory | PPR | Hit | Text |
|---|---|---|---|---|
| 1 | `m14` | 0.00427 | ✓ | David works at Amazon as a product manager. His office is at… |
| 2 | `m13` | 0.00337 |  | Sam's brother David lives in Seattle. |
| 3 | `m36` | 0.00267 |  | David will also fly to Boston for Maria's birthday. |
| 4 | `m34` | 0.00210 |  | Sam booked flights to Boston for May 13 through 17 to be the… |
| 5 | `m37` | 0.00176 |  | Sam's Spanish practice has slipped to once a week since star… |

## Search subgraph

Seeds from filtered triples (red), top-PPR phrases (blue), top-5 passage nodes (green if required, grey otherwise).

```mermaid
graph LR
    n1(["Amazon"]):::seed
    n29(["Seattle"]):::seed
    n6(["David"]):::seed
    n25["Sam"]:::phrase
    n4["Boston"]:::phrase
    n63["side project"]:::phrase
    n56["other companies"]:::phrase
    n30["Spanish"]:::phrase
    n61["scraper"]:::phrase
    n0["Alex"]:::phrase
    n11["March"]:::phrase
    n32["StartupCo"]:::phrase
    n39["burned out"]:::phrase
    g82["m14: David works at Amazon as a product …"]:::hit
    g81["m13: Sam's brother David lives in Seattl…"]:::passage
    g104["m36: David will also fly to Boston for M…"]:::passage
    g102["m34: Sam booked flights to Boston for Ma…"]:::passage
    g105["m37: Sam's Spanish practice has slipped …"]:::passage
    n1 --- n29
    n1 --- n6
    n1 --- n25
    n1 --- n4
    n1 --- n63
    n1 --- n56
    n1 --- n30
    n1 --- n61
    n1 --- n11
    n1 --- n32
    n1 --- n39
    n29 --- n63
    n29 --- n56
    n29 --- n30
    n29 --- n61
    n29 --- n32
    n29 --- n39
    n6 --- n29
    n6 --- n25
    n6 --- n63
    n6 --- n56
    n6 --- n30
    n6 --- n61
    n6 --- n11
    n6 --- n32
    n6 --- n39
    n25 --- n29
    n25 --- n63
    n25 --- n56
    n25 --- n30
    n25 --- n61
    n25 --- n32
    n25 --- n39
    n4 --- n29
    n4 --- n6
    n4 --- n25
    n4 --- n63
    n4 --- n56
    n4 --- n30
    n4 --- n61
    n4 --- n11
    n4 --- n32
    n4 --- n39
    n56 --- n63
    n56 --- n61
    n30 --- n63
    n30 --- n56
    n30 --- n61
    n30 --- n32
    n30 --- n39
    n61 --- n63
    n0 --- n1
    n0 --- n29
    n0 --- n6
    n0 --- n25
    n0 --- n4
    n0 --- n63
    n0 --- n56
    n0 --- n30
    n0 --- n61
    n0 --- n11
    n0 --- n32
    n0 --- n39
    n11 --- n29
    n11 --- n25
    n11 --- n63
    n11 --- n56
    n11 --- n30
    n11 --- n61
    n11 --- n32
    n11 --- n39
    n32 --- n63
    n32 --- n56
    n32 --- n61
    n32 --- n39
    n39 --- n63
    n39 --- n56
    n39 --- n61
    n1 -.-> g82
    n29 -.-> g81
    n29 -.-> g82
    n6 -.-> g104
    n6 -.-> g81
    n6 -.-> g82
    n25 -.-> g102
    n25 -.-> g105
    n25 -.-> g81
    n4 -.-> g102
    n4 -.-> g104
    n30 -.-> g105
    n32 -.-> g105
    classDef seed fill:#fdd,stroke:#c44,stroke-width:2px
    classDef phrase fill:#eef,stroke:#446
    classDef passage fill:#f5f5f5,stroke:#666
    classDef hit fill:#dfd,stroke:#080,stroke-width:3px
```
