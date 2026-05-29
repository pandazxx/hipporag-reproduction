# Trace — q17  [compositional_aggregation, expect=HippoRAG]

**Question:** Who are all the people Sam has mentioned in conversations?

**Expected answer:** Alex (partner), Jennifer (old manager), Maria (mother), David (brother), Marcus (new manager)

**Required facts:** ['m03', 'm05', 'm11', 'm13', 'm28']

## Step 1 — query→triple top-K (cosine on triple-text embeddings)

| Cosine | Subject | Predicate | Object |
|---|---|---|---|
| 0.412 | `Sam` | uses | `Duolingo` |
| 0.407 | `Sam` | interviewed at | `developer-tools startups` |
| 0.402 | `Sam` | is planning trip with | `Alex` |
| 0.393 | `Sam` | is planning trip to | `Joshua Tree` |
| 0.391 | `Sam` | is going to be there for | `Maria's birthday` |
| 0.381 | `Yosemite` | was visited by | `Sam` |
| 0.378 | `Sam` | plans to visit | `Maria` |
| 0.377 | `Sam` | climbed with | `Alex` |
| 0.377 | `Sam` | is planning trip in | `March` |
| 0.374 | `Sam` | has manager | `Jennifer` |

## Step 2 — recognition memory (LLM filter)

| Subject | Predicate | Object |
|---|---|---|
| `Sam` | is planning trip with | `Alex` |
| `Sam` | is going to be there for | `Maria's birthday` |
| `Sam` | plans to visit | `Maria` |
| `Sam` | climbed with | `Alex` |

## Step 3 — top 5 retrieved passages

| Rank | Memory | PPR | Hit | Text |
|---|---|---|---|---|
| 1 | `m34` | 0.00315 |  | Sam booked flights to Boston for May 13 through 17 to be the… |
| 2 | `m15` | 0.00292 |  | Sam plans to visit Maria for her birthday in mid-May. |
| 3 | `m40` | 0.00276 |  | Sam is planning a long climbing trip to Joshua Tree in late … |
| 4 | `m22` | 0.00273 |  | Sam climbed with Alex at Yosemite. Alex is also a climber bu… |
| 5 | `m35` | 0.00239 |  | Alex will join Sam on the Boston trip. |

## Search subgraph

Seeds from filtered triples (red), top-PPR phrases (blue), top-5 passage nodes (green if required, grey otherwise).

```mermaid
graph LR
    n0(["Alex"]):::seed
    n25(["Sam"]):::seed
    n13(["Maria"]):::seed
    n14(["Maria's birthday"]):::seed
    n4["Boston"]:::phrase
    n63["side project"]:::phrase
    n30["Spanish"]:::phrase
    n56["other companies"]:::phrase
    n11["March"]:::phrase
    n61["scraper"]:::phrase
    n32["StartupCo"]:::phrase
    n1["Amazon"]:::phrase
    n40["climber"]:::phrase
    n39["burned out"]:::phrase
    g102["m34: Sam booked flights to Boston for Ma…"]:::passage
    g83["m15: Sam plans to visit Maria for her bi…"]:::passage
    g108["m40: Sam is planning a long climbing tri…"]:::passage
    g90["m22: Sam climbed with Alex at Yosemite. …"]:::passage
    g103["m35: Alex will join Sam on the Boston tr…"]:::passage
    n0 --- n25
    n0 --- n13
    n0 --- n14
    n0 --- n4
    n0 --- n63
    n0 --- n30
    n0 --- n56
    n0 --- n11
    n0 --- n61
    n0 --- n32
    n0 --- n1
    n0 --- n40
    n0 --- n39
    n25 --- n63
    n25 --- n30
    n25 --- n56
    n25 --- n61
    n25 --- n32
    n25 --- n40
    n25 --- n39
    n13 --- n25
    n13 --- n14
    n13 --- n63
    n13 --- n30
    n13 --- n56
    n13 --- n61
    n13 --- n32
    n13 --- n40
    n13 --- n39
    n14 --- n25
    n14 --- n63
    n14 --- n30
    n14 --- n56
    n14 --- n61
    n14 --- n40
    n14 --- n39
    n4 --- n25
    n4 --- n13
    n4 --- n14
    n4 --- n63
    n4 --- n30
    n4 --- n56
    n4 --- n11
    n4 --- n61
    n4 --- n32
    n4 --- n40
    n4 --- n39
    n30 --- n63
    n30 --- n56
    n30 --- n61
    n30 --- n32
    n30 --- n40
    n30 --- n39
    n56 --- n63
    n56 --- n61
    n11 --- n25
    n11 --- n13
    n11 --- n14
    n11 --- n63
    n11 --- n30
    n11 --- n56
    n11 --- n61
    n11 --- n32
    n11 --- n40
    n11 --- n39
    n61 --- n63
    n32 --- n63
    n32 --- n56
    n32 --- n61
    n32 --- n40
    n32 --- n39
    n1 --- n25
    n1 --- n13
    n1 --- n14
    n1 --- n4
    n1 --- n63
    n1 --- n30
    n1 --- n56
    n1 --- n11
    n1 --- n61
    n1 --- n32
    n1 --- n40
    n1 --- n39
    n40 --- n63
    n40 --- n56
    n40 --- n61
    n39 --- n63
    n39 --- n56
    n39 --- n61
    n39 --- n40
    n0 -.-> g103
    n0 -.-> g108
    n0 -.-> g90
    n25 -.-> g102
    n25 -.-> g103
    n25 -.-> g108
    n25 -.-> g83
    n25 -.-> g90
    n13 -.-> g83
    n14 -.-> g102
    n14 -.-> g83
    n4 -.-> g102
    n4 -.-> g103
    n11 -.-> g108
    n40 -.-> g90
    classDef seed fill:#fdd,stroke:#c44,stroke-width:2px
    classDef phrase fill:#eef,stroke:#446
    classDef passage fill:#f5f5f5,stroke:#666
    classDef hit fill:#dfd,stroke:#080,stroke-width:3px
```
