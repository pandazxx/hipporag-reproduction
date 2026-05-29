# Trace — q22  [absence_abstention, expect=tie]

**Question:** What is Sam's salary at StartupCo?

**Expected answer:** unknown / not mentioned

**Required facts:** (none — absence/abstention)

## Step 1 — query→triple top-K (cosine on triple-text embeddings)

| Cosine | Subject | Predicate | Object |
|---|---|---|---|
| 0.619 | `Sam` | works at | `StartupCo` |
| 0.619 | `Sam` | works at | `StartupCo` |
| 0.589 | `Sam` | accepted offer from | `StartupCo` |
| 0.582 | `Sam` | started at | `StartupCo` |
| 0.573 | `Sam` | received job offer from | `StartupCo` |
| 0.493 | `Sam` | works at | `TechCorp` |
| 0.493 | `Sam` | works at | `TechCorp` |
| 0.493 | `Sam` | works at | `TechCorp` |
| 0.476 | `StartupCo` | based in | `San Francisco` |
| 0.444 | `Sam` | gave notice at | `TechCorp` |

## Step 2 — recognition memory (LLM filter)

_(LLM kept no triples)_

## Step 3 — top 5 retrieved passages

| Rank | Memory | PPR | Hit | Text |
|---|---|---|---|---|
| 1 | `m29` | 0.00766 |  | Sam started at StartupCo today. The role is senior backend e… |
| 2 | `m25` | 0.00746 |  | Sam got a job offer from StartupCo, a developer-tools startu… |
| 3 | `m27` | 0.00741 |  | Sam accepted the StartupCo offer and gave notice at TechCorp… |
| 4 | `m37` | 0.00732 |  | Sam's Spanish practice has slipped to once a week since star… |
| 5 | `m30` | 0.00707 |  | Sam is now learning Rust because StartupCo's main service is… |

## Search subgraph

Seeds from filtered triples (red), top-PPR phrases (blue), top-5 passage nodes (green if required, grey otherwise).

```mermaid
graph LR
    n25["Sam"]:::phrase
    n32["StartupCo"]:::phrase
    n33["TechCorp"]:::phrase
    n0["Alex"]:::phrase
    n30["Spanish"]:::phrase
    n4["Boston"]:::phrase
    n61["scraper"]:::phrase
    n56["other companies"]:::phrase
    n13["Maria"]:::phrase
    n11["March"]:::phrase
    g97["m29: Sam started at StartupCo today. The…"]:::passage
    g93["m25: Sam got a job offer from StartupCo,…"]:::passage
    g95["m27: Sam accepted the StartupCo offer an…"]:::passage
    g105["m37: Sam's Spanish practice has slipped …"]:::passage
    g98["m30: Sam is now learning Rust because St…"]:::passage
    n25 --- n32
    n25 --- n33
    n25 --- n30
    n25 --- n61
    n25 --- n56
    n32 --- n33
    n32 --- n61
    n32 --- n56
    n33 --- n61
    n33 --- n56
    n0 --- n25
    n0 --- n32
    n0 --- n33
    n0 --- n30
    n0 --- n4
    n0 --- n61
    n0 --- n56
    n0 --- n13
    n0 --- n11
    n30 --- n32
    n30 --- n33
    n30 --- n61
    n30 --- n56
    n4 --- n25
    n4 --- n32
    n4 --- n33
    n4 --- n30
    n4 --- n61
    n4 --- n56
    n4 --- n13
    n4 --- n11
    n56 --- n61
    n13 --- n25
    n13 --- n32
    n13 --- n33
    n13 --- n30
    n13 --- n61
    n13 --- n56
    n11 --- n25
    n11 --- n32
    n11 --- n33
    n11 --- n30
    n11 --- n61
    n11 --- n56
    n11 --- n13
    n25 -.-> g105
    n25 -.-> g93
    n25 -.-> g95
    n25 -.-> g97
    n25 -.-> g98
    n32 -.-> g105
    n32 -.-> g93
    n32 -.-> g95
    n32 -.-> g97
    n32 -.-> g98
    n33 -.-> g95
    n30 -.-> g105
    classDef seed fill:#fdd,stroke:#c44,stroke-width:2px
    classDef phrase fill:#eef,stroke:#446
    classDef passage fill:#f5f5f5,stroke:#666
    classDef hit fill:#dfd,stroke:#080,stroke-width:3px
```
