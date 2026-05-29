# Trace — q10  [deep_multi_hop, expect=tie]

**Question:** In which city was the person born who is married to the graphic designer's partner's brother?

**Expected answer:** unknown / cannot determine (Maria's birth location is not in the facts)

**Required facts:** (none — absence/abstention)

## Step 1 — query→triple top-K (cosine on triple-text embeddings)

| Cosine | Subject | Predicate | Object |
|---|---|---|---|
| 0.338 | `Sam` | has partner | `Alex` |
| 0.315 | `Alex` | works as | `graphic designer` |
| 0.260 | `Sam` | is | `software engineer` |
| 0.259 | `David` | is brother of | `Sam` |
| 0.256 | `David` | has office at | `Seattle` |
| 0.251 | `David` | will attend | `Maria's birthday` |
| 0.245 | `Alex` | will accompany | `Sam` |
| 0.242 | `Sam` | has mother | `Maria` |
| 0.237 | `Jennifer` | works at | `TechCorp` |
| 0.237 | `Sam` | has manager | `Jennifer` |

## Step 2 — recognition memory (LLM filter)

| Subject | Predicate | Object |
|---|---|---|
| `David` | is brother of | `Sam` |
| `Sam` | has partner | `Alex` |
| `Alex` | works as | `graphic designer` |

## Step 3 — top 5 retrieved passages

| Rank | Memory | PPR | Hit | Text |
|---|---|---|---|---|
| 1 | `m05` | 0.00313 |  | Sam's partner is Alex. Alex works as a graphic designer. |
| 2 | `m40` | 0.00260 |  | Sam is planning a long climbing trip to Joshua Tree in late … |
| 3 | `m22` | 0.00256 |  | Sam climbed with Alex at Yosemite. Alex is also a climber bu… |
| 4 | `m34` | 0.00241 |  | Sam booked flights to Boston for May 13 through 17 to be the… |
| 5 | `m35` | 0.00230 |  | Alex will join Sam on the Boston trip. |

## Search subgraph

Seeds from filtered triples (red), top-PPR phrases (blue), top-5 passage nodes (green if required, grey otherwise).

```mermaid
graph LR
    n0(["Alex"]):::seed
    n25(["Sam"]):::seed
    n50(["graphic designer"]):::seed
    n6(["David"]):::seed
    n63["side project"]:::phrase
    n4["Boston"]:::phrase
    n56["other companies"]:::phrase
    n30["Spanish"]:::phrase
    n11["March"]:::phrase
    n61["scraper"]:::phrase
    n1["Amazon"]:::phrase
    n32["StartupCo"]:::phrase
    n40["climber"]:::phrase
    n39["burned out"]:::phrase
    g73["m05: Sam's partner is Alex. Alex works a…"]:::passage
    g108["m40: Sam is planning a long climbing tri…"]:::passage
    g90["m22: Sam climbed with Alex at Yosemite. …"]:::passage
    g102["m34: Sam booked flights to Boston for Ma…"]:::passage
    g103["m35: Alex will join Sam on the Boston tr…"]:::passage
    n0 --- n25
    n0 --- n50
    n0 --- n6
    n0 --- n63
    n0 --- n4
    n0 --- n56
    n0 --- n30
    n0 --- n11
    n0 --- n61
    n0 --- n1
    n0 --- n32
    n0 --- n40
    n0 --- n39
    n25 --- n50
    n25 --- n63
    n25 --- n56
    n25 --- n30
    n25 --- n61
    n25 --- n32
    n25 --- n40
    n25 --- n39
    n50 --- n63
    n50 --- n56
    n50 --- n61
    n6 --- n25
    n6 --- n50
    n6 --- n63
    n6 --- n56
    n6 --- n30
    n6 --- n11
    n6 --- n61
    n6 --- n32
    n6 --- n40
    n6 --- n39
    n4 --- n25
    n4 --- n50
    n4 --- n6
    n4 --- n63
    n4 --- n56
    n4 --- n30
    n4 --- n11
    n4 --- n61
    n4 --- n32
    n4 --- n40
    n4 --- n39
    n56 --- n63
    n56 --- n61
    n30 --- n50
    n30 --- n63
    n30 --- n56
    n30 --- n61
    n30 --- n32
    n30 --- n40
    n30 --- n39
    n11 --- n25
    n11 --- n50
    n11 --- n63
    n11 --- n56
    n11 --- n30
    n11 --- n61
    n11 --- n32
    n11 --- n40
    n11 --- n39
    n61 --- n63
    n1 --- n25
    n1 --- n50
    n1 --- n6
    n1 --- n63
    n1 --- n4
    n1 --- n56
    n1 --- n30
    n1 --- n11
    n1 --- n61
    n1 --- n32
    n1 --- n40
    n1 --- n39
    n32 --- n50
    n32 --- n63
    n32 --- n56
    n32 --- n61
    n32 --- n40
    n32 --- n39
    n40 --- n50
    n40 --- n63
    n40 --- n56
    n40 --- n61
    n39 --- n50
    n39 --- n63
    n39 --- n56
    n39 --- n61
    n39 --- n40
    n0 -.-> g103
    n0 -.-> g73
    n0 -.-> g108
    n0 -.-> g90
    n25 -.-> g102
    n25 -.-> g103
    n25 -.-> g73
    n25 -.-> g108
    n25 -.-> g90
    n50 -.-> g73
    n4 -.-> g102
    n4 -.-> g103
    n11 -.-> g108
    n40 -.-> g90
    classDef seed fill:#fdd,stroke:#c44,stroke-width:2px
    classDef phrase fill:#eef,stroke:#446
    classDef passage fill:#f5f5f5,stroke:#666
    classDef hit fill:#dfd,stroke:#080,stroke-width:3px
```
