# Trace — q11  [implicit_conceptual, expect=A-Mem]

**Question:** What outdoor activities does Sam enjoy?

**Expected answer:** rock climbing (Yosemite, Joshua Tree, Berkeley Ironworks — though gym is indoor)

**Required facts:** ['m08', 'm21', 'm40', 'm38']

## Step 1 — query→triple top-K (cosine on triple-text embeddings)

| Cosine | Subject | Predicate | Object |
|---|---|---|---|
| 0.533 | `Sam` | has goal | `discover new outdoor climbing destinations` |
| 0.508 | `Sam` | has been doing | `rock climbing` |
| 0.494 | `Sam` | went climbing at | `Berkeley Ironworks` |
| 0.478 | `Sam` | climbed at | `Yosemite` |
| 0.462 | `Sam` | goes rock climbing at | `Berkeley Ironworks` |
| 0.454 | `Sam` | has favorite climbing problems | `V4-V5 boulder routes` |
| 0.433 | `Sam` | uses | `Duolingo` |
| 0.413 | `Sam` | practices | `Spanish` |
| 0.413 | `Sam` | practices | `Spanish` |
| 0.412 | `Sam` | lives in | `California` |

## Step 2 — recognition memory (LLM filter)

| Subject | Predicate | Object |
|---|---|---|
| `Sam` | has goal | `discover new outdoor climbing destinations` |
| `Sam` | has been doing | `rock climbing` |
| `Sam` | went climbing at | `Berkeley Ironworks` |
| `Sam` | climbed at | `Yosemite` |

## Step 3 — top 5 retrieved passages

| Rank | Memory | PPR | Hit | Text |
|---|---|---|---|---|
| 1 | `m08` | 0.00891 | ✓ | Sam goes rock climbing at Berkeley Ironworks gym. |
| 2 | `m38` | 0.00883 | ✓ | Sam went climbing at Berkeley Ironworks this morning, first … |
| 3 | `m20` | 0.00385 |  | Sam's goal with the scraper is to discover new outdoor climb… |
| 4 | `m22` | 0.00284 |  | Sam climbed with Alex at Yosemite. Alex is also a climber bu… |
| 5 | `m34` | 0.00265 |  | Sam booked flights to Boston for May 13 through 17 to be the… |

## Search subgraph

Seeds from filtered triples (red), top-PPR phrases (blue), top-5 passage nodes (green if required, grey otherwise).

```mermaid
graph LR
    n3(["Berkeley Ironworks"]):::seed
    n37(["Yosemite"]):::seed
    n46(["discover new outdoor climbing destinations"]):::seed
    n25(["Sam"]):::seed
    n60(["rock climbing"]):::seed
    n61["scraper"]:::phrase
    n56["other companies"]:::phrase
    n63["side project"]:::phrase
    n40["climber"]:::phrase
    n0["Alex"]:::phrase
    n30["Spanish"]:::phrase
    n32["StartupCo"]:::phrase
    n11["March"]:::phrase
    n4["Boston"]:::phrase
    n20["MountainProject.com"]:::phrase
    g76["m08: Sam goes rock climbing at Berkeley …"]:::hit
    g106["m38: Sam went climbing at Berkeley Ironw…"]:::hit
    g88["m20: Sam's goal with the scraper is to d…"]:::passage
    g90["m22: Sam climbed with Alex at Yosemite. …"]:::passage
    g102["m34: Sam booked flights to Boston for Ma…"]:::passage
    n3 --- n25
    n37 --- n60
    n37 --- n61
    n37 --- n56
    n37 --- n63
    n37 --- n40
    n46 --- n60
    n46 --- n61
    n46 --- n56
    n25 --- n37
    n25 --- n46
    n25 --- n60
    n25 --- n61
    n25 --- n56
    n25 --- n63
    n25 --- n40
    n25 --- n30
    n25 --- n32
    n60 --- n61
    n60 --- n63
    n61 --- n63
    n56 --- n60
    n56 --- n61
    n56 --- n63
    n40 --- n46
    n40 --- n60
    n40 --- n61
    n40 --- n56
    n40 --- n63
    n0 --- n37
    n0 --- n25
    n0 --- n60
    n0 --- n61
    n0 --- n56
    n0 --- n63
    n0 --- n40
    n0 --- n30
    n0 --- n32
    n0 --- n11
    n0 --- n4
    n0 --- n20
    n30 --- n37
    n30 --- n60
    n30 --- n61
    n30 --- n56
    n30 --- n63
    n30 --- n40
    n30 --- n32
    n32 --- n60
    n32 --- n61
    n32 --- n56
    n32 --- n63
    n32 --- n40
    n11 --- n37
    n11 --- n25
    n11 --- n60
    n11 --- n61
    n11 --- n56
    n11 --- n63
    n11 --- n40
    n11 --- n30
    n11 --- n32
    n11 --- n20
    n4 --- n37
    n4 --- n25
    n4 --- n60
    n4 --- n61
    n4 --- n56
    n4 --- n63
    n4 --- n40
    n4 --- n30
    n4 --- n32
    n4 --- n11
    n4 --- n20
    n20 --- n37
    n20 --- n46
    n20 --- n25
    n20 --- n60
    n20 --- n61
    n20 --- n56
    n20 --- n63
    n20 --- n40
    n20 --- n30
    n20 --- n32
    n3 -.-> g106
    n3 -.-> g76
    n37 -.-> g90
    n46 -.-> g88
    n25 -.-> g102
    n25 -.-> g106
    n25 -.-> g76
    n25 -.-> g88
    n25 -.-> g90
    n61 -.-> g88
    n40 -.-> g90
    n0 -.-> g90
    n4 -.-> g102
    classDef seed fill:#fdd,stroke:#c44,stroke-width:2px
    classDef phrase fill:#eef,stroke:#446
    classDef passage fill:#f5f5f5,stroke:#666
    classDef hit fill:#dfd,stroke:#080,stroke-width:3px
```
