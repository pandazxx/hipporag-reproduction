# Trace — q07  [two_hop, expect=tie]

**Question:** What does Sam's mother do for a living, and where does she live?

**Expected answer:** high school chemistry teacher in Boston

**Required facts:** ['m11', 'm12']

## Step 1 — query→triple top-K (cosine on triple-text embeddings)

| Cosine | Subject | Predicate | Object |
|---|---|---|---|
| 0.444 | `Sam` | has mother | `Maria` |
| 0.415 | `Sam` | lives in | `Oakland` |
| 0.414 | `Sam` | works at | `TechCorp` |
| 0.414 | `Sam` | works at | `TechCorp` |
| 0.414 | `Sam` | works at | `TechCorp` |
| 0.407 | `Sam` | lives in | `California` |
| 0.399 | `Sam` | works at | `StartupCo` |
| 0.399 | `Sam` | works at | `StartupCo` |
| 0.372 | `Sam` | has manager | `Jennifer` |
| 0.365 | `Sam` | practices | `Spanish` |

## Step 2 — recognition memory (LLM filter)

| Subject | Predicate | Object |
|---|---|---|
| `Sam` | has mother | `Maria` |

## Step 3 — top 5 retrieved passages

| Rank | Memory | PPR | Hit | Text |
|---|---|---|---|---|
| 1 | `m11` | 0.00419 | ✓ | Sam's mother Maria lives in Boston. |
| 2 | `m15` | 0.00390 |  | Sam plans to visit Maria for her birthday in mid-May. |
| 3 | `m34` | 0.00307 |  | Sam booked flights to Boston for May 13 through 17 to be the… |
| 4 | `m08` | 0.00292 |  | Sam goes rock climbing at Berkeley Ironworks gym. |
| 5 | `m23` | 0.00292 |  | Sam is feeling burned out at TechCorp due to long hours and … |

## Search subgraph

Seeds from filtered triples (red), top-PPR phrases (blue), top-5 passage nodes (green if required, grey otherwise).

```mermaid
graph LR
    n25(["Sam"]):::seed
    n13(["Maria"]):::seed
    n32["StartupCo"]:::phrase
    n4["Boston"]:::phrase
    n0["Alex"]:::phrase
    n30["Spanish"]:::phrase
    n63["side project"]:::phrase
    n56["other companies"]:::phrase
    n61["scraper"]:::phrase
    n11["March"]:::phrase
    n1["Amazon"]:::phrase
    n39["burned out"]:::phrase
    g79["m11: Sam's mother Maria lives in Boston."]:::hit
    g83["m15: Sam plans to visit Maria for her bi…"]:::passage
    g102["m34: Sam booked flights to Boston for Ma…"]:::passage
    g76["m08: Sam goes rock climbing at Berkeley …"]:::passage
    g91["m23: Sam is feeling burned out at TechCo…"]:::passage
    n25 --- n32
    n25 --- n30
    n25 --- n63
    n25 --- n56
    n25 --- n61
    n25 --- n39
    n13 --- n25
    n13 --- n32
    n13 --- n30
    n13 --- n63
    n13 --- n56
    n13 --- n61
    n13 --- n39
    n32 --- n63
    n32 --- n56
    n32 --- n61
    n32 --- n39
    n4 --- n25
    n4 --- n13
    n4 --- n32
    n4 --- n30
    n4 --- n63
    n4 --- n56
    n4 --- n61
    n4 --- n11
    n4 --- n39
    n0 --- n25
    n0 --- n13
    n0 --- n32
    n0 --- n4
    n0 --- n30
    n0 --- n63
    n0 --- n56
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
    n61 --- n63
    n11 --- n25
    n11 --- n13
    n11 --- n32
    n11 --- n30
    n11 --- n63
    n11 --- n56
    n11 --- n61
    n11 --- n39
    n1 --- n25
    n1 --- n13
    n1 --- n32
    n1 --- n4
    n1 --- n30
    n1 --- n63
    n1 --- n56
    n1 --- n61
    n1 --- n11
    n1 --- n39
    n39 --- n63
    n39 --- n56
    n39 --- n61
    n25 -.-> g102
    n25 -.-> g76
    n25 -.-> g79
    n25 -.-> g83
    n25 -.-> g91
    n13 -.-> g79
    n13 -.-> g83
    n4 -.-> g102
    n4 -.-> g79
    n39 -.-> g91
    classDef seed fill:#fdd,stroke:#c44,stroke-width:2px
    classDef phrase fill:#eef,stroke:#446
    classDef passage fill:#f5f5f5,stroke:#666
    classDef hit fill:#dfd,stroke:#080,stroke-width:3px
```
