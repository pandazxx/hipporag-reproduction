# Trace — q12  [implicit_conceptual, expect=A-Mem]

**Question:** What Python libraries has Sam used?

**Expected answer:** BeautifulSoup

**Required facts:** ['m17', 'm18']

## Step 1 — query→triple top-K (cosine on triple-text embeddings)

| Cosine | Subject | Predicate | Object |
|---|---|---|---|
| 0.556 | `Sam` | uses | `BeautifulSoup` |
| 0.547 | `Sam` | worked on | `web scraper project` |
| 0.528 | `Sam` | uses | `scraper` |
| 0.513 | `Sam` | uses | `Duolingo` |
| 0.497 | `Sam` | decided to use | `Python` |
| 0.460 | `Sam` | is | `software engineer` |
| 0.454 | `Sam` | has role | `senior backend engineer` |
| 0.448 | `Sam` | is using | `scraper` |
| 0.440 | `Sam` | interviewed at | `developer-tools startups` |
| 0.439 | `Sam` | started at | `StartupCo` |

## Step 2 — recognition memory (LLM filter)

| Subject | Predicate | Object |
|---|---|---|
| `Sam` | uses | `BeautifulSoup` |
| `Sam` | uses | `scraper` |
| `Sam` | decided to use | `Python` |

## Step 3 — top 5 retrieved passages

| Rank | Memory | PPR | Hit | Text |
|---|---|---|---|---|
| 1 | `m32` | 0.00299 |  | Sam is using the reqwest and scraper crates for the Rust ver… |
| 2 | `m18` | 0.00275 | ✓ | Sam uses the BeautifulSoup library for parsing HTML in the s… |
| 3 | `m20` | 0.00270 |  | Sam's goal with the scraper is to discover new outdoor climb… |
| 4 | `m17` | 0.00259 | ✓ | Sam decided to use Python for the web scraper project. |
| 5 | `m34` | 0.00256 |  | Sam booked flights to Boston for May 13 through 17 to be the… |

## Search subgraph

Seeds from filtered triples (red), top-PPR phrases (blue), top-5 passage nodes (green if required, grey otherwise).

```mermaid
graph LR
    n25(["Sam"]):::seed
    n2(["BeautifulSoup"]):::seed
    n61(["scraper"]):::seed
    n22(["Python"]):::seed
    n63["side project"]:::phrase
    n56["other companies"]:::phrase
    n30["Spanish"]:::phrase
    n0["Alex"]:::phrase
    n32["StartupCo"]:::phrase
    n11["March"]:::phrase
    n4["Boston"]:::phrase
    n7["Duolingo"]:::phrase
    n1["Amazon"]:::phrase
    n39["burned out"]:::phrase
    g100["m32: Sam is using the reqwest and scrape…"]:::passage
    g86["m18: Sam uses the BeautifulSoup library …"]:::hit
    g88["m20: Sam's goal with the scraper is to d…"]:::passage
    g85["m17: Sam decided to use Python for the w…"]:::hit
    g102["m34: Sam booked flights to Boston for Ma…"]:::passage
    n25 --- n61
    n25 --- n63
    n25 --- n56
    n25 --- n30
    n25 --- n32
    n25 --- n39
    n2 --- n25
    n2 --- n61
    n2 --- n22
    n2 --- n63
    n2 --- n56
    n2 --- n30
    n2 --- n11
    n2 --- n4
    n2 --- n7
    n2 --- n39
    n61 --- n63
    n22 --- n25
    n22 --- n61
    n22 --- n63
    n22 --- n56
    n22 --- n30
    n22 --- n32
    n22 --- n39
    n56 --- n61
    n56 --- n63
    n30 --- n61
    n30 --- n63
    n30 --- n56
    n30 --- n32
    n30 --- n39
    n0 --- n25
    n0 --- n2
    n0 --- n61
    n0 --- n22
    n0 --- n63
    n0 --- n56
    n0 --- n30
    n0 --- n32
    n0 --- n11
    n0 --- n4
    n0 --- n7
    n0 --- n1
    n0 --- n39
    n32 --- n61
    n32 --- n63
    n32 --- n56
    n32 --- n39
    n11 --- n25
    n11 --- n61
    n11 --- n22
    n11 --- n63
    n11 --- n56
    n11 --- n30
    n11 --- n32
    n11 --- n39
    n4 --- n25
    n4 --- n61
    n4 --- n22
    n4 --- n63
    n4 --- n56
    n4 --- n30
    n4 --- n32
    n4 --- n11
    n4 --- n7
    n4 --- n39
    n7 --- n25
    n7 --- n61
    n7 --- n22
    n7 --- n63
    n7 --- n56
    n7 --- n30
    n7 --- n32
    n7 --- n11
    n7 --- n39
    n1 --- n25
    n1 --- n2
    n1 --- n61
    n1 --- n22
    n1 --- n63
    n1 --- n56
    n1 --- n30
    n1 --- n32
    n1 --- n11
    n1 --- n4
    n1 --- n7
    n1 --- n39
    n39 --- n61
    n39 --- n63
    n39 --- n56
    n25 -.-> g102
    n25 -.-> g85
    n25 -.-> g86
    n25 -.-> g88
    n25 -.-> g100
    n2 -.-> g86
    n61 -.-> g88
    n61 -.-> g100
    n22 -.-> g85
    n4 -.-> g102
    classDef seed fill:#fdd,stroke:#c44,stroke-width:2px
    classDef phrase fill:#eef,stroke:#446
    classDef passage fill:#f5f5f5,stroke:#666
    classDef hit fill:#dfd,stroke:#080,stroke-width:3px
```
