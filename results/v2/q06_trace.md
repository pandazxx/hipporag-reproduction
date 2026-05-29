# Trace — q06  [two_hop, expect=tie]

**Question:** What programming language does Sam's web scraper use?

**Expected answer:** Python (initially), then rewritten in Rust

**Required facts:** ['m17', 'm31']

## Step 1 — query→triple top-K (cosine on triple-text embeddings)

| Cosine | Subject | Predicate | Object |
|---|---|---|---|
| 0.555 | `Sam` | worked on | `web scraper project` |
| 0.540 | `Sam` | uses | `scraper` |
| 0.515 | `Sam` | uses | `BeautifulSoup` |
| 0.503 | `scraper` | is written in | `Rust` |
| 0.494 | `Sam` | uses | `Duolingo` |
| 0.493 | `Sam` | is using | `scraper` |
| 0.472 | `Sam` | decided to rewrite | `climbing scraper` |
| 0.468 | `Sam` | decided to use | `Python` |
| 0.453 | `Sam` | practices | `Spanish` |
| 0.453 | `Sam` | practices | `Spanish` |

## Step 2 — recognition memory (LLM filter)

| Subject | Predicate | Object |
|---|---|---|
| `Sam` | decided to use | `Python` |

## Step 3 — top 5 retrieved passages

| Rank | Memory | PPR | Hit | Text |
|---|---|---|---|---|
| 1 | `m17` | 0.00437 | ✓ | Sam decided to use Python for the web scraper project. |
| 2 | `m32` | 0.00358 |  | Sam is using the reqwest and scraper crates for the Rust ver… |
| 3 | `m16` | 0.00318 |  | Sam started a side project: building a web scraper to find n… |
| 4 | `m20` | 0.00310 |  | Sam's goal with the scraper is to discover new outdoor climb… |
| 5 | `m18` | 0.00308 |  | Sam uses the BeautifulSoup library for parsing HTML in the s… |

## Search subgraph

Seeds from filtered triples (red), top-PPR phrases (blue), top-5 passage nodes (green if required, grey otherwise).

```mermaid
graph LR
    n25(["Sam"]):::seed
    n22(["Python"]):::seed
    n32["StartupCo"]:::phrase
    n61["scraper"]:::phrase
    n63["side project"]:::phrase
    n30["Spanish"]:::phrase
    n0["Alex"]:::phrase
    n56["other companies"]:::phrase
    n4["Boston"]:::phrase
    n11["March"]:::phrase
    n7["Duolingo"]:::phrase
    n1["Amazon"]:::phrase
    g85["m17: Sam decided to use Python for the w…"]:::hit
    g100["m32: Sam is using the reqwest and scrape…"]:::passage
    g84["m16: Sam started a side project: buildin…"]:::passage
    g88["m20: Sam's goal with the scraper is to d…"]:::passage
    g86["m18: Sam uses the BeautifulSoup library …"]:::passage
    n25 --- n32
    n25 --- n61
    n25 --- n63
    n25 --- n30
    n25 --- n56
    n22 --- n25
    n22 --- n32
    n22 --- n61
    n22 --- n63
    n22 --- n30
    n22 --- n56
    n32 --- n61
    n32 --- n63
    n32 --- n56
    n61 --- n63
    n30 --- n32
    n30 --- n61
    n30 --- n63
    n30 --- n56
    n0 --- n25
    n0 --- n22
    n0 --- n32
    n0 --- n61
    n0 --- n63
    n0 --- n30
    n0 --- n56
    n0 --- n4
    n0 --- n11
    n0 --- n7
    n0 --- n1
    n56 --- n61
    n56 --- n63
    n4 --- n25
    n4 --- n22
    n4 --- n32
    n4 --- n61
    n4 --- n63
    n4 --- n30
    n4 --- n56
    n4 --- n11
    n4 --- n7
    n11 --- n25
    n11 --- n22
    n11 --- n32
    n11 --- n61
    n11 --- n63
    n11 --- n30
    n11 --- n56
    n7 --- n25
    n7 --- n22
    n7 --- n32
    n7 --- n61
    n7 --- n63
    n7 --- n30
    n7 --- n56
    n7 --- n11
    n1 --- n25
    n1 --- n22
    n1 --- n32
    n1 --- n61
    n1 --- n63
    n1 --- n30
    n1 --- n56
    n1 --- n4
    n1 --- n11
    n1 --- n7
    n25 -.-> g84
    n25 -.-> g85
    n25 -.-> g86
    n25 -.-> g88
    n25 -.-> g100
    n22 -.-> g85
    n61 -.-> g88
    n61 -.-> g100
    n63 -.-> g84
    classDef seed fill:#fdd,stroke:#c44,stroke-width:2px
    classDef phrase fill:#eef,stroke:#446
    classDef passage fill:#f5f5f5,stroke:#666
    classDef hit fill:#dfd,stroke:#080,stroke-width:3px
```
