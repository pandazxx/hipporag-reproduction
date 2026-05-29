# Trace — q03  [single_hop, expect=tie]

**Question:** When is Maria's birthday?

**Expected answer:** May 15

**Required facts:** ['m33']

## Step 1 — query→triple top-K (cosine on triple-text embeddings)

| Cosine | Subject | Predicate | Object |
|---|---|---|---|
| 0.590 | `Maria` | has birthday on | `May 15` |
| 0.588 | `Maria` | has birthday in | `May` |
| 0.583 | `Maria's birthday` | is in | `Boston` |
| 0.577 | `Maria's birthday` | is on | `May 13` |
| 0.443 | `David` | will attend | `Maria's birthday` |
| 0.414 | `Maria` | works as | `high school chemistry teacher` |
| 0.412 | `Maria` | lives in | `Boston` |
| 0.406 | `Sam` | is going to be there for | `Maria's birthday` |
| 0.368 | `Sam` | visiting for | `Maria's birthday` |
| 0.334 | `Sam` | plans to visit | `Maria` |

## Step 2 — recognition memory (LLM filter)

| Subject | Predicate | Object |
|---|---|---|
| `Maria` | has birthday on | `May 15` |
| `Maria` | has birthday in | `May` |
| `Maria's birthday` | is on | `May 13` |

## Step 3 — top 5 retrieved passages

| Rank | Memory | PPR | Hit | Text |
|---|---|---|---|---|
| 1 | `m15` | 0.00367 |  | Sam plans to visit Maria for her birthday in mid-May. |
| 2 | `m34` | 0.00357 |  | Sam booked flights to Boston for May 13 through 17 to be the… |
| 3 | `m33` | 0.00289 | ✓ | Maria's birthday is May 15. |
| 4 | `m11` | 0.00209 |  | Sam's mother Maria lives in Boston. |
| 5 | `m36` | 0.00203 |  | David will also fly to Boston for Maria's birthday. |

## Search subgraph

Seeds from filtered triples (red), top-PPR phrases (blue), top-5 passage nodes (green if required, grey otherwise).

```mermaid
graph LR
    n13(["Maria"]):::seed
    n14(["Maria's birthday"]):::seed
    n15(["May"]):::seed
    n16(["May 13"]):::seed
    n17(["May 15"]):::seed
    n25["Sam"]:::phrase
    n4["Boston"]:::phrase
    n63["side project"]:::phrase
    n56["other companies"]:::phrase
    n30["Spanish"]:::phrase
    n61["scraper"]:::phrase
    n11["March"]:::phrase
    n1["Amazon"]:::phrase
    n0["Alex"]:::phrase
    n39["burned out"]:::phrase
    g83["m15: Sam plans to visit Maria for her bi…"]:::passage
    g102["m34: Sam booked flights to Boston for Ma…"]:::passage
    g101["m33: Maria's birthday is May 15."]:::hit
    g79["m11: Sam's mother Maria lives in Boston."]:::passage
    g104["m36: David will also fly to Boston for M…"]:::passage
    n13 --- n14
    n13 --- n15
    n13 --- n16
    n13 --- n17
    n13 --- n25
    n13 --- n63
    n13 --- n56
    n13 --- n30
    n13 --- n61
    n13 --- n39
    n14 --- n15
    n14 --- n16
    n14 --- n17
    n14 --- n25
    n14 --- n63
    n14 --- n56
    n14 --- n30
    n14 --- n61
    n14 --- n39
    n15 --- n16
    n15 --- n17
    n15 --- n25
    n15 --- n63
    n15 --- n56
    n15 --- n30
    n15 --- n61
    n15 --- n39
    n16 --- n17
    n16 --- n25
    n16 --- n63
    n16 --- n56
    n16 --- n30
    n16 --- n61
    n16 --- n39
    n17 --- n25
    n17 --- n63
    n17 --- n56
    n17 --- n30
    n17 --- n61
    n17 --- n39
    n25 --- n63
    n25 --- n56
    n25 --- n30
    n25 --- n61
    n25 --- n39
    n4 --- n13
    n4 --- n14
    n4 --- n15
    n4 --- n16
    n4 --- n17
    n4 --- n25
    n4 --- n63
    n4 --- n56
    n4 --- n30
    n4 --- n61
    n4 --- n11
    n4 --- n39
    n56 --- n63
    n56 --- n61
    n30 --- n63
    n30 --- n56
    n30 --- n61
    n30 --- n39
    n61 --- n63
    n11 --- n13
    n11 --- n14
    n11 --- n15
    n11 --- n16
    n11 --- n17
    n11 --- n25
    n11 --- n63
    n11 --- n56
    n11 --- n30
    n11 --- n61
    n11 --- n39
    n1 --- n13
    n1 --- n14
    n1 --- n15
    n1 --- n16
    n1 --- n17
    n1 --- n25
    n1 --- n4
    n1 --- n63
    n1 --- n56
    n1 --- n30
    n1 --- n61
    n1 --- n11
    n1 --- n39
    n0 --- n13
    n0 --- n14
    n0 --- n15
    n0 --- n16
    n0 --- n17
    n0 --- n25
    n0 --- n4
    n0 --- n63
    n0 --- n56
    n0 --- n30
    n0 --- n61
    n0 --- n11
    n0 --- n1
    n0 --- n39
    n39 --- n63
    n39 --- n56
    n39 --- n61
    n13 -.-> g101
    n13 -.-> g79
    n13 -.-> g83
    n14 -.-> g102
    n14 -.-> g104
    n14 -.-> g83
    n15 -.-> g83
    n16 -.-> g102
    n17 -.-> g101
    n25 -.-> g102
    n25 -.-> g79
    n25 -.-> g83
    n4 -.-> g102
    n4 -.-> g104
    n4 -.-> g79
    classDef seed fill:#fdd,stroke:#c44,stroke-width:2px
    classDef phrase fill:#eef,stroke:#446
    classDef passage fill:#f5f5f5,stroke:#666
    classDef hit fill:#dfd,stroke:#080,stroke-width:3px
```
