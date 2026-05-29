# Trace — q02  [single_hop, expect=tie]

**Question:** What is Maria's profession?

**Expected answer:** high school chemistry teacher

**Required facts:** ['m12']

## Step 1 — query→triple top-K (cosine on triple-text embeddings)

| Cosine | Subject | Predicate | Object |
|---|---|---|---|
| 0.523 | `Maria` | works as | `high school chemistry teacher` |
| 0.461 | `Maria` | has birthday in | `May` |
| 0.458 | `Maria` | has birthday on | `May 15` |
| 0.450 | `Maria's birthday` | is on | `May 13` |
| 0.436 | `Maria` | lives in | `Boston` |
| 0.427 | `Maria's birthday` | is in | `Boston` |
| 0.351 | `David` | will attend | `Maria's birthday` |
| 0.327 | `Sam` | plans to visit | `Maria` |
| 0.326 | `Sam` | is going to be there for | `Maria's birthday` |
| 0.323 | `Sam` | has mother | `Maria` |

## Step 2 — recognition memory (LLM filter)

| Subject | Predicate | Object |
|---|---|---|
| `Maria` | works as | `high school chemistry teacher` |

## Step 3 — top 5 retrieved passages

| Rank | Memory | PPR | Hit | Text |
|---|---|---|---|---|
| 1 | `m12` | 0.00561 | ✓ | Maria works as a high school chemistry teacher. |
| 2 | `m15` | 0.00340 |  | Sam plans to visit Maria for her birthday in mid-May. |
| 3 | `m33` | 0.00327 |  | Maria's birthday is May 15. |
| 4 | `m11` | 0.00308 |  | Sam's mother Maria lives in Boston. |
| 5 | `m34` | 0.00255 |  | Sam booked flights to Boston for May 13 through 17 to be the… |

## Search subgraph

Seeds from filtered triples (red), top-PPR phrases (blue), top-5 passage nodes (green if required, grey otherwise).

```mermaid
graph LR
    n51(["high school chemistry teacher"]):::seed
    n13(["Maria"]):::seed
    n25["Sam"]:::phrase
    n4["Boston"]:::phrase
    n63["side project"]:::phrase
    n30["Spanish"]:::phrase
    n61["scraper"]:::phrase
    n56["other companies"]:::phrase
    n1["Amazon"]:::phrase
    n11["March"]:::phrase
    n39["burned out"]:::phrase
    n7["Duolingo"]:::phrase
    g80["m12: Maria works as a high school chemis…"]:::hit
    g83["m15: Sam plans to visit Maria for her bi…"]:::passage
    g101["m33: Maria's birthday is May 15."]:::passage
    g79["m11: Sam's mother Maria lives in Boston."]:::passage
    g102["m34: Sam booked flights to Boston for Ma…"]:::passage
    n51 --- n63
    n51 --- n61
    n51 --- n56
    n13 --- n51
    n13 --- n25
    n13 --- n63
    n13 --- n30
    n13 --- n61
    n13 --- n56
    n13 --- n39
    n25 --- n63
    n25 --- n30
    n25 --- n61
    n25 --- n56
    n25 --- n39
    n4 --- n51
    n4 --- n13
    n4 --- n25
    n4 --- n63
    n4 --- n30
    n4 --- n61
    n4 --- n56
    n4 --- n11
    n4 --- n39
    n4 --- n7
    n30 --- n51
    n30 --- n63
    n30 --- n61
    n30 --- n56
    n30 --- n39
    n61 --- n63
    n56 --- n63
    n56 --- n61
    n1 --- n51
    n1 --- n13
    n1 --- n25
    n1 --- n4
    n1 --- n63
    n1 --- n30
    n1 --- n61
    n1 --- n56
    n1 --- n11
    n1 --- n39
    n1 --- n7
    n11 --- n51
    n11 --- n13
    n11 --- n25
    n11 --- n63
    n11 --- n30
    n11 --- n61
    n11 --- n56
    n11 --- n39
    n39 --- n51
    n39 --- n63
    n39 --- n61
    n39 --- n56
    n7 --- n51
    n7 --- n13
    n7 --- n25
    n7 --- n63
    n7 --- n30
    n7 --- n61
    n7 --- n56
    n7 --- n11
    n7 --- n39
    n51 -.-> g80
    n13 -.-> g101
    n13 -.-> g79
    n13 -.-> g80
    n13 -.-> g83
    n25 -.-> g102
    n25 -.-> g79
    n25 -.-> g83
    n4 -.-> g102
    n4 -.-> g79
    classDef seed fill:#fdd,stroke:#c44,stroke-width:2px
    classDef phrase fill:#eef,stroke:#446
    classDef passage fill:#f5f5f5,stroke:#666
    classDef hit fill:#dfd,stroke:#080,stroke-width:3px
```
