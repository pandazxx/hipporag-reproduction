# Trace — q18  [compositional_aggregation, expect=HippoRAG]

**Question:** What different programming languages and libraries has Sam used or learned?

**Expected answer:** Python, BeautifulSoup, Rust, reqwest, scraper

**Required facts:** ['m17', 'm18', 'm30', 'm32']

## Step 1 — query→triple top-K (cosine on triple-text embeddings)

| Cosine | Subject | Predicate | Object |
|---|---|---|---|
| 0.560 | `Sam` | uses | `Duolingo` |
| 0.544 | `Sam` | worked on | `web scraper project` |
| 0.507 | `Sam` | uses | `BeautifulSoup` |
| 0.483 | `Sam` | is | `software engineer` |
| 0.483 | `Sam` | decided to use | `Python` |
| 0.479 | `Sam` | uses | `scraper` |
| 0.466 | `Sam` | practices | `Spanish` |
| 0.466 | `Sam` | practices | `Spanish` |
| 0.460 | `Sam` | has favorite climbing problems | `V4-V5 boulder routes` |
| 0.456 | `Sam` | started learning Spanish | `two months ago` |

## Step 2 — recognition memory (LLM filter)

| Subject | Predicate | Object |
|---|---|---|
| `Sam` | decided to use | `Python` |
| `Sam` | uses | `BeautifulSoup` |

## Step 3 — top 5 retrieved passages

| Rank | Memory | PPR | Hit | Text |
|---|---|---|---|---|
| 1 | `m18` | 0.00317 | ✓ | Sam uses the BeautifulSoup library for parsing HTML in the s… |
| 2 | `m17` | 0.00298 | ✓ | Sam decided to use Python for the web scraper project. |
| 3 | `m32` | 0.00281 | ✓ | Sam is using the reqwest and scraper crates for the Rust ver… |
| 4 | `m34` | 0.00274 |  | Sam booked flights to Boston for May 13 through 17 to be the… |
| 5 | `m16` | 0.00268 |  | Sam started a side project: building a web scraper to find n… |

## Search subgraph

Seeds from filtered triples (red), top-PPR phrases (blue), top-5 passage nodes (green if required, grey otherwise).

```mermaid
graph LR
    n25(["Sam"]):::seed
    n2(["BeautifulSoup"]):::seed
    n22(["Python"]):::seed
    n63["side project"]:::phrase
    n61["scraper"]:::phrase
    n30["Spanish"]:::phrase
    n56["other companies"]:::phrase
    n0["Alex"]:::phrase
    n32["StartupCo"]:::phrase
    n11["March"]:::phrase
    n4["Boston"]:::phrase
    n7["Duolingo"]:::phrase
    n1["Amazon"]:::phrase
    g86["m18: Sam uses the BeautifulSoup library …"]:::hit
    g85["m17: Sam decided to use Python for the w…"]:::hit
    g100["m32: Sam is using the reqwest and scrape…"]:::hit
    g102["m34: Sam booked flights to Boston for Ma…"]:::passage
    g84["m16: Sam started a side project: buildin…"]:::passage
    n25 --- n63
    n25 --- n61
    n25 --- n30
    n25 --- n56
    n25 --- n32
    n2 --- n25
    n2 --- n22
    n2 --- n63
    n2 --- n61
    n2 --- n30
    n2 --- n56
    n2 --- n11
    n2 --- n4
    n2 --- n7
    n22 --- n25
    n22 --- n63
    n22 --- n61
    n22 --- n30
    n22 --- n56
    n22 --- n32
    n61 --- n63
    n30 --- n63
    n30 --- n61
    n30 --- n56
    n30 --- n32
    n56 --- n63
    n56 --- n61
    n0 --- n25
    n0 --- n2
    n0 --- n22
    n0 --- n63
    n0 --- n61
    n0 --- n30
    n0 --- n56
    n0 --- n32
    n0 --- n11
    n0 --- n4
    n0 --- n7
    n0 --- n1
    n32 --- n63
    n32 --- n61
    n32 --- n56
    n11 --- n25
    n11 --- n22
    n11 --- n63
    n11 --- n61
    n11 --- n30
    n11 --- n56
    n11 --- n32
    n4 --- n25
    n4 --- n22
    n4 --- n63
    n4 --- n61
    n4 --- n30
    n4 --- n56
    n4 --- n32
    n4 --- n11
    n4 --- n7
    n7 --- n25
    n7 --- n22
    n7 --- n63
    n7 --- n61
    n7 --- n30
    n7 --- n56
    n7 --- n32
    n7 --- n11
    n1 --- n25
    n1 --- n2
    n1 --- n22
    n1 --- n63
    n1 --- n61
    n1 --- n30
    n1 --- n56
    n1 --- n32
    n1 --- n11
    n1 --- n4
    n1 --- n7
    n25 -.-> g102
    n25 -.-> g84
    n25 -.-> g85
    n25 -.-> g86
    n25 -.-> g100
    n2 -.-> g86
    n22 -.-> g85
    n63 -.-> g84
    n61 -.-> g100
    n4 -.-> g102
    classDef seed fill:#fdd,stroke:#c44,stroke-width:2px
    classDef phrase fill:#eef,stroke:#446
    classDef passage fill:#f5f5f5,stroke:#666
    classDef hit fill:#dfd,stroke:#080,stroke-width:3px
```
