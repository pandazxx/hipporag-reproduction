# Trace — q16  [information_update, expect=A-Mem]

**Question:** What language is Sam's climbing scraper currently written in?

**Expected answer:** Rust

**Required facts:** ['m17', 'm31']

## Step 1 — query→triple top-K (cosine on triple-text embeddings)

| Cosine | Subject | Predicate | Object |
|---|---|---|---|
| 0.596 | `Sam` | decided to rewrite | `climbing scraper` |
| 0.529 | `scraper` | is used to | `discover new outdoor climbing destinations` |
| 0.508 | `Rust` | is used for | `climbing scraper` |
| 0.506 | `scraper` | is written in | `Rust` |
| 0.489 | `web scraper` | used for | `finding new climbing destinations` |
| 0.479 | `Sam` | worked on | `web scraper project` |
| 0.479 | `Sam` | uses | `scraper` |
| 0.470 | `Sam` | has favorite climbing problems | `V4-V5 boulder routes` |
| 0.469 | `Sam` | uses | `BeautifulSoup` |
| 0.461 | `Sam` | uses | `Duolingo` |

## Step 2 — recognition memory (LLM filter)

| Subject | Predicate | Object |
|---|---|---|
| `scraper` | is written in | `Rust` |

## Step 3 — top 5 retrieved passages

| Rank | Memory | PPR | Hit | Text |
|---|---|---|---|---|
| 1 | `m32` | 0.00518 |  | Sam is using the reqwest and scraper crates for the Rust ver… |
| 2 | `m31` | 0.00397 | ✓ | Sam decided to rewrite the climbing scraper in Rust as a lea… |
| 3 | `m20` | 0.00391 |  | Sam's goal with the scraper is to discover new outdoor climb… |
| 4 | `m30` | 0.00336 |  | Sam is now learning Rust because StartupCo's main service is… |
| 5 | `m19` | 0.00317 |  | The scraper collects climbing route data from MountainProjec… |

## Search subgraph

Seeds from filtered triples (red), top-PPR phrases (blue), top-5 passage nodes (green if required, grey otherwise).

```mermaid
graph LR
    n61(["scraper"]):::seed
    n23(["Rust"]):::seed
    n25["Sam"]:::phrase
    n32["StartupCo"]:::phrase
    n63["side project"]:::phrase
    n30["Spanish"]:::phrase
    n56["other companies"]:::phrase
    n0["Alex"]:::phrase
    n11["March"]:::phrase
    n1["Amazon"]:::phrase
    n7["Duolingo"]:::phrase
    n4["Boston"]:::phrase
    g100["m32: Sam is using the reqwest and scrape…"]:::passage
    g99["m31: Sam decided to rewrite the climbing…"]:::hit
    g88["m20: Sam's goal with the scraper is to d…"]:::passage
    g98["m30: Sam is now learning Rust because St…"]:::passage
    g87["m19: The scraper collects climbing route…"]:::passage
    n61 --- n63
    n23 --- n61
    n23 --- n25
    n23 --- n32
    n23 --- n63
    n23 --- n30
    n23 --- n56
    n25 --- n61
    n25 --- n32
    n25 --- n63
    n25 --- n30
    n25 --- n56
    n32 --- n61
    n32 --- n63
    n32 --- n56
    n30 --- n61
    n30 --- n32
    n30 --- n63
    n30 --- n56
    n56 --- n61
    n56 --- n63
    n0 --- n61
    n0 --- n23
    n0 --- n25
    n0 --- n32
    n0 --- n63
    n0 --- n30
    n0 --- n56
    n0 --- n11
    n0 --- n1
    n0 --- n7
    n0 --- n4
    n11 --- n61
    n11 --- n23
    n11 --- n25
    n11 --- n32
    n11 --- n63
    n11 --- n30
    n11 --- n56
    n1 --- n61
    n1 --- n23
    n1 --- n25
    n1 --- n32
    n1 --- n63
    n1 --- n30
    n1 --- n56
    n1 --- n11
    n1 --- n7
    n1 --- n4
    n7 --- n61
    n7 --- n23
    n7 --- n25
    n7 --- n32
    n7 --- n63
    n7 --- n30
    n7 --- n56
    n7 --- n11
    n4 --- n61
    n4 --- n23
    n4 --- n25
    n4 --- n32
    n4 --- n63
    n4 --- n30
    n4 --- n56
    n4 --- n11
    n4 --- n7
    n61 -.-> g87
    n61 -.-> g88
    n61 -.-> g100
    n23 -.-> g98
    n23 -.-> g99
    n23 -.-> g100
    n25 -.-> g88
    n25 -.-> g98
    n25 -.-> g99
    n25 -.-> g100
    n32 -.-> g98
    classDef seed fill:#fdd,stroke:#c44,stroke-width:2px
    classDef phrase fill:#eef,stroke:#446
    classDef passage fill:#f5f5f5,stroke:#666
    classDef hit fill:#dfd,stroke:#080,stroke-width:3px
```
