# Trace — q14  [information_update, expect=A-Mem]

**Question:** Where does Sam currently work?

**Expected answer:** StartupCo

**Required facts:** ['m27', 'm29']

## Step 1 — query→triple top-K (cosine on triple-text embeddings)

| Cosine | Subject | Predicate | Object |
|---|---|---|---|
| 0.497 | `Sam` | works at | `StartupCo` |
| 0.497 | `Sam` | works at | `StartupCo` |
| 0.490 | `Sam` | works at | `TechCorp` |
| 0.490 | `Sam` | works at | `TechCorp` |
| 0.490 | `Sam` | works at | `TechCorp` |
| 0.474 | `Sam` | worked on | `web scraper project` |
| 0.471 | `Sam` | is | `software engineer` |
| 0.465 | `Sam` | lives in | `California` |
| 0.465 | `Sam` | has role | `senior backend engineer` |
| 0.450 | `Sam` | lives in | `Oakland` |

## Step 2 — recognition memory (LLM filter)

| Subject | Predicate | Object |
|---|---|---|
| `Sam` | works at | `StartupCo` |
| `Sam` | works at | `TechCorp` |

## Step 3 — top 5 retrieved passages

| Rank | Memory | PPR | Hit | Text |
|---|---|---|---|---|
| 1 | `m27` | 0.00341 | ✓ | Sam accepted the StartupCo offer and gave notice at TechCorp… |
| 2 | `m23` | 0.00336 |  | Sam is feeling burned out at TechCorp due to long hours and … |
| 3 | `m37` | 0.00314 |  | Sam's Spanish practice has slipped to once a week since star… |
| 4 | `m01` | 0.00305 |  | Sam works as a software engineer at TechCorp. |
| 5 | `m03` | 0.00285 |  | Sam's manager at TechCorp is Jennifer. |

## Search subgraph

Seeds from filtered triples (red), top-PPR phrases (blue), top-5 passage nodes (green if required, grey otherwise).

```mermaid
graph LR
    n32(["StartupCo"]):::seed
    n25(["Sam"]):::seed
    n33(["TechCorp"]):::seed
    n30["Spanish"]:::phrase
    n63["side project"]:::phrase
    n0["Alex"]:::phrase
    n56["other companies"]:::phrase
    n61["scraper"]:::phrase
    n11["March"]:::phrase
    n4["Boston"]:::phrase
    n1["Amazon"]:::phrase
    n39["burned out"]:::phrase
    n7["Duolingo"]:::phrase
    g95["m27: Sam accepted the StartupCo offer an…"]:::hit
    g91["m23: Sam is feeling burned out at TechCo…"]:::passage
    g105["m37: Sam's Spanish practice has slipped …"]:::passage
    g69["m01: Sam works as a software engineer at…"]:::passage
    g71["m03: Sam's manager at TechCorp is Jennif…"]:::passage
    n32 --- n33
    n32 --- n63
    n32 --- n56
    n32 --- n61
    n32 --- n39
    n25 --- n32
    n25 --- n33
    n25 --- n30
    n25 --- n63
    n25 --- n56
    n25 --- n61
    n25 --- n39
    n33 --- n63
    n33 --- n56
    n33 --- n61
    n33 --- n39
    n30 --- n32
    n30 --- n33
    n30 --- n63
    n30 --- n56
    n30 --- n61
    n30 --- n39
    n0 --- n32
    n0 --- n25
    n0 --- n33
    n0 --- n30
    n0 --- n63
    n0 --- n56
    n0 --- n61
    n0 --- n11
    n0 --- n4
    n0 --- n1
    n0 --- n39
    n0 --- n7
    n56 --- n63
    n56 --- n61
    n61 --- n63
    n11 --- n32
    n11 --- n25
    n11 --- n33
    n11 --- n30
    n11 --- n63
    n11 --- n56
    n11 --- n61
    n11 --- n39
    n4 --- n32
    n4 --- n25
    n4 --- n33
    n4 --- n30
    n4 --- n63
    n4 --- n56
    n4 --- n61
    n4 --- n11
    n4 --- n39
    n4 --- n7
    n1 --- n32
    n1 --- n25
    n1 --- n33
    n1 --- n30
    n1 --- n63
    n1 --- n56
    n1 --- n61
    n1 --- n11
    n1 --- n4
    n1 --- n39
    n1 --- n7
    n39 --- n63
    n39 --- n56
    n39 --- n61
    n7 --- n32
    n7 --- n25
    n7 --- n33
    n7 --- n30
    n7 --- n63
    n7 --- n56
    n7 --- n61
    n7 --- n11
    n7 --- n39
    n32 -.-> g105
    n32 -.-> g95
    n25 -.-> g69
    n25 -.-> g71
    n25 -.-> g105
    n25 -.-> g91
    n25 -.-> g95
    n33 -.-> g69
    n33 -.-> g71
    n33 -.-> g91
    n33 -.-> g95
    n30 -.-> g105
    n39 -.-> g91
    classDef seed fill:#fdd,stroke:#c44,stroke-width:2px
    classDef phrase fill:#eef,stroke:#446
    classDef passage fill:#f5f5f5,stroke:#666
    classDef hit fill:#dfd,stroke:#080,stroke-width:3px
```
