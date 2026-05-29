# Trace — q15  [information_update, expect=A-Mem]

**Question:** Who is Sam's current manager?

**Expected answer:** Marcus

**Required facts:** ['m28', 'm29']

## Step 1 — query→triple top-K (cosine on triple-text embeddings)

| Cosine | Subject | Predicate | Object |
|---|---|---|---|
| 0.546 | `Sam` | has manager | `Marcus` |
| 0.542 | `Sam` | has manager | `Jennifer` |
| 0.507 | `Jennifer` | is manager of | `Sam` |
| 0.507 | `Marcus` | is manager of | `Sam` |
| 0.419 | `Sam` | has role | `senior backend engineer` |
| 0.415 | `Sam` | works at | `StartupCo` |
| 0.415 | `Sam` | works at | `StartupCo` |
| 0.414 | `Sam` | uses | `Duolingo` |
| 0.413 | `Sam` | is | `software engineer` |
| 0.396 | `Sam` | has been doing | `rock climbing` |

## Step 2 — recognition memory (LLM filter)

| Subject | Predicate | Object |
|---|---|---|
| `Sam` | has manager | `Marcus` |
| `Sam` | has manager | `Jennifer` |
| `Jennifer` | is manager of | `Sam` |
| `Marcus` | is manager of | `Sam` |

## Step 3 — top 5 retrieved passages

| Rank | Memory | PPR | Hit | Text |
|---|---|---|---|---|
| 1 | `m28` | 0.00319 | ✓ | Sam's new manager at StartupCo will be Marcus. |
| 2 | `m03` | 0.00274 |  | Sam's manager at TechCorp is Jennifer. |
| 3 | `m34` | 0.00268 |  | Sam booked flights to Boston for May 13 through 17 to be the… |
| 4 | `m37` | 0.00236 |  | Sam's Spanish practice has slipped to once a week since star… |
| 5 | `m23` | 0.00234 |  | Sam is feeling burned out at TechCorp due to long hours and … |

## Search subgraph

Seeds from filtered triples (red), top-PPR phrases (blue), top-5 passage nodes (green if required, grey otherwise).

```mermaid
graph LR
    n8(["Jennifer"]):::seed
    n25(["Sam"]):::seed
    n12(["Marcus"]):::seed
    n32["StartupCo"]:::phrase
    n0["Alex"]:::phrase
    n63["side project"]:::phrase
    n30["Spanish"]:::phrase
    n56["other companies"]:::phrase
    n61["scraper"]:::phrase
    n4["Boston"]:::phrase
    n11["March"]:::phrase
    n1["Amazon"]:::phrase
    n39["burned out"]:::phrase
    g96["m28: Sam's new manager at StartupCo will…"]:::hit
    g71["m03: Sam's manager at TechCorp is Jennif…"]:::passage
    g102["m34: Sam booked flights to Boston for Ma…"]:::passage
    g105["m37: Sam's Spanish practice has slipped …"]:::passage
    g91["m23: Sam is feeling burned out at TechCo…"]:::passage
    n8 --- n25
    n8 --- n12
    n8 --- n32
    n8 --- n63
    n8 --- n30
    n8 --- n56
    n8 --- n61
    n8 --- n11
    n8 --- n39
    n25 --- n32
    n25 --- n63
    n25 --- n30
    n25 --- n56
    n25 --- n61
    n25 --- n39
    n12 --- n25
    n12 --- n32
    n12 --- n63
    n12 --- n30
    n12 --- n56
    n12 --- n61
    n12 --- n39
    n32 --- n63
    n32 --- n56
    n32 --- n61
    n32 --- n39
    n0 --- n8
    n0 --- n25
    n0 --- n12
    n0 --- n32
    n0 --- n63
    n0 --- n30
    n0 --- n56
    n0 --- n61
    n0 --- n4
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
    n4 --- n8
    n4 --- n25
    n4 --- n12
    n4 --- n32
    n4 --- n63
    n4 --- n30
    n4 --- n56
    n4 --- n61
    n4 --- n11
    n4 --- n39
    n11 --- n25
    n11 --- n12
    n11 --- n32
    n11 --- n63
    n11 --- n30
    n11 --- n56
    n11 --- n61
    n11 --- n39
    n1 --- n8
    n1 --- n25
    n1 --- n12
    n1 --- n32
    n1 --- n63
    n1 --- n30
    n1 --- n56
    n1 --- n61
    n1 --- n4
    n1 --- n11
    n1 --- n39
    n39 --- n63
    n39 --- n56
    n39 --- n61
    n8 -.-> g71
    n25 -.-> g102
    n25 -.-> g71
    n25 -.-> g105
    n25 -.-> g91
    n25 -.-> g96
    n12 -.-> g96
    n32 -.-> g105
    n32 -.-> g96
    n30 -.-> g105
    n4 -.-> g102
    n39 -.-> g91
    classDef seed fill:#fdd,stroke:#c44,stroke-width:2px
    classDef phrase fill:#eef,stroke:#446
    classDef passage fill:#f5f5f5,stroke:#666
    classDef hit fill:#dfd,stroke:#080,stroke-width:3px
```
