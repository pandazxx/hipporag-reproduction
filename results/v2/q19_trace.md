# Trace — q19  [compositional_aggregation, expect=HippoRAG]

**Question:** What places does Sam have travel or residence connections to?

**Expected answer:** Oakland (lives), San Francisco (work), Boston (mother + planned trip), Seattle (brother), Yosemite (climbed), Joshua Tree (planned trip), Mexico (Spanish learning motivation)

**Required facts:** ['m02', 'm04', 'm06', 'm11', 'm13', 'm21', 'm34', 'm40']

## Step 1 — query→triple top-K (cosine on triple-text embeddings)

| Cosine | Subject | Predicate | Object |
|---|---|---|---|
| 0.439 | `Yosemite` | was visited by | `Sam` |
| 0.439 | `Sam` | lives in | `Oakland` |
| 0.439 | `Sam` | lives in | `California` |
| 0.438 | `Sam` | booked flights to | `Boston` |
| 0.426 | `Sam` | climbed at | `Yosemite` |
| 0.422 | `Sam` | uses | `Duolingo` |
| 0.422 | `Sam` | went climbing at | `Berkeley Ironworks` |
| 0.416 | `Sam` | has goal | `discover new outdoor climbing destinations` |
| 0.406 | `Sam` | will travel to | `Boston` |
| 0.403 | `Sam` | works at | `StartupCo` |

## Step 2 — recognition memory (LLM filter)

| Subject | Predicate | Object |
|---|---|---|
| `Yosemite` | was visited by | `Sam` |
| `Sam` | lives in | `Oakland` |
| `Sam` | lives in | `California` |
| `Sam` | booked flights to | `Boston` |

## Step 3 — top 5 retrieved passages

| Rank | Memory | PPR | Hit | Text |
|---|---|---|---|---|
| 1 | `m34` | 0.00298 | ✓ | Sam booked flights to Boston for May 13 through 17 to be the… |
| 2 | `m04` | 0.00272 | ✓ | Sam lives in Oakland, California. |
| 3 | `m22` | 0.00270 |  | Sam climbed with Alex at Yosemite. Alex is also a climber bu… |
| 4 | `m16` | 0.00232 |  | Sam started a side project: building a web scraper to find n… |
| 5 | `m37` | 0.00230 |  | Sam's Spanish practice has slipped to once a week since star… |

## Search subgraph

Seeds from filtered triples (red), top-PPR phrases (blue), top-5 passage nodes (green if required, grey otherwise).

```mermaid
graph LR
    n4(["Boston"]):::seed
    n5(["California"]):::seed
    n37(["Yosemite"]):::seed
    n21(["Oakland"]):::seed
    n25(["Sam"]):::seed
    n0["Alex"]:::phrase
    n63["side project"]:::phrase
    n30["Spanish"]:::phrase
    n56["other companies"]:::phrase
    n61["scraper"]:::phrase
    n11["March"]:::phrase
    n32["StartupCo"]:::phrase
    n1["Amazon"]:::phrase
    n7["Duolingo"]:::phrase
    n39["burned out"]:::phrase
    g102["m34: Sam booked flights to Boston for Ma…"]:::hit
    g72["m04: Sam lives in Oakland, California."]:::hit
    g90["m22: Sam climbed with Alex at Yosemite. …"]:::passage
    g84["m16: Sam started a side project: buildin…"]:::passage
    g105["m37: Sam's Spanish practice has slipped …"]:::passage
    n4 --- n5
    n4 --- n37
    n4 --- n21
    n4 --- n25
    n4 --- n63
    n4 --- n30
    n4 --- n56
    n4 --- n61
    n4 --- n11
    n4 --- n32
    n4 --- n7
    n4 --- n39
    n5 --- n37
    n5 --- n21
    n5 --- n25
    n5 --- n63
    n5 --- n30
    n5 --- n56
    n5 --- n61
    n5 --- n11
    n5 --- n32
    n5 --- n7
    n5 --- n39
    n37 --- n63
    n37 --- n56
    n37 --- n61
    n37 --- n39
    n21 --- n37
    n21 --- n25
    n21 --- n63
    n21 --- n30
    n21 --- n56
    n21 --- n61
    n21 --- n32
    n21 --- n39
    n25 --- n37
    n25 --- n63
    n25 --- n30
    n25 --- n56
    n25 --- n61
    n25 --- n32
    n25 --- n39
    n0 --- n4
    n0 --- n5
    n0 --- n37
    n0 --- n21
    n0 --- n25
    n0 --- n63
    n0 --- n30
    n0 --- n56
    n0 --- n61
    n0 --- n11
    n0 --- n32
    n0 --- n1
    n0 --- n7
    n0 --- n39
    n30 --- n37
    n30 --- n63
    n30 --- n56
    n30 --- n61
    n30 --- n32
    n30 --- n39
    n56 --- n63
    n56 --- n61
    n61 --- n63
    n11 --- n37
    n11 --- n21
    n11 --- n25
    n11 --- n63
    n11 --- n30
    n11 --- n56
    n11 --- n61
    n11 --- n32
    n11 --- n39
    n32 --- n63
    n32 --- n56
    n32 --- n61
    n32 --- n39
    n1 --- n4
    n1 --- n5
    n1 --- n37
    n1 --- n21
    n1 --- n25
    n1 --- n63
    n1 --- n30
    n1 --- n56
    n1 --- n61
    n1 --- n11
    n1 --- n32
    n1 --- n7
    n1 --- n39
    n7 --- n37
    n7 --- n21
    n7 --- n25
    n7 --- n63
    n7 --- n30
    n7 --- n56
    n7 --- n61
    n7 --- n11
    n7 --- n32
    n7 --- n39
    n39 --- n63
    n39 --- n56
    n39 --- n61
    n4 -.-> g102
    n5 -.-> g72
    n37 -.-> g90
    n21 -.-> g72
    n25 -.-> g102
    n25 -.-> g72
    n25 -.-> g105
    n25 -.-> g84
    n25 -.-> g90
    n0 -.-> g90
    n63 -.-> g84
    n30 -.-> g105
    n32 -.-> g105
    classDef seed fill:#fdd,stroke:#c44,stroke-width:2px
    classDef phrase fill:#eef,stroke:#446
    classDef passage fill:#f5f5f5,stroke:#666
    classDef hit fill:#dfd,stroke:#080,stroke-width:3px
```
