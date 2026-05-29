# HippoRAG 2 memory graph

- **Memories indexed:** 40
- **Phrase nodes:** 69
- **Passage nodes:** 40
- **Total graph nodes:** 109
- **Triples extracted:** 112

## Phrase subgraph (top 30 of 69 by degree)

Shows relation + synonymy edges among the most-connected phrases. Passage and context edges are omitted for clarity.

```mermaid
graph LR
    n56["other companies"]
    n63["side project"]
    n1["Amazon"]
    n39["burned out"]
    n7["Duolingo"]
    n53["long hours"]
    n40["climber"]
    n25["Sam"]
    n30["Spanish"]
    n61["scraper"]
    n11["March"]
    n60["rock climbing"]
    n20["MountainProject.com"]
    n19["Mexico"]
    n4["Boston"]
    n64["software engineer"]
    n66["two months ago"]
    n49["fully remote work"]
    n31["Spanish practice"]
    n0["Alex"]
    n34["V4 routes"]
    n5["California"]
    n67["web scraper"]
    n6["David"]
    n15["May"]
    n38["building a web scraper"]
    n36["V5 routes"]
    n65["three years"]
    n68["web scraper project"]
    n32["StartupCo"]
    n56 --- n63
    n56 --- n61
    n56 --- n60
    n56 --- n64
    n56 --- n66
    n56 --- n67
    n56 --- n65
    n56 --- n68
    n63 --- n64
    n63 --- n66
    n63 --- n67
    n63 --- n65
    n63 --- n68
    n1 --- n56
    n1 --- n63
    n1 --- n39
    n1 --- n7
    n1 --- n53
    n1 --- n40
    n1 --- n25
    n1 --- n30
    n1 --- n61
    n1 --- n11
    n1 --- n60
    n1 --- n20
    n1 --- n19
    n1 --- n4
    n1 --- n64
    n1 --- n66
    n1 --- n49
    n1 --- n31
    n1 --- n34
    n1 --- n5
    n1 --- n67
    n1 --- n6
    n1 --- n15
    n1 --- n38
    n1 --- n36
    n1 --- n65
    n1 --- n68
    n1 --- n32
    n39 --- n56
    n39 --- n63
    n39 --- n53
    n39 --- n40
    n39 --- n61
    n39 --- n60
    n39 --- n64
    n39 --- n66
    n39 --- n49
    n39 --- n67
    n39 --- n65
    n39 --- n68
    n7 --- n56
    n7 --- n63
    n7 --- n39
    n7 --- n53
    n7 --- n40
    n7 --- n25
    n7 --- n30
    n7 --- n61
    n7 --- n11
    n7 --- n60
    n7 --- n20
    n7 --- n19
    n7 --- n64
    n7 --- n66
    n7 --- n49
    n7 --- n31
    n7 --- n34
    n7 --- n67
    n7 --- n15
    n7 --- n38
    n7 --- n36
    n7 --- n65
    n7 --- n68
    n7 --- n32
    n53 --- n56
    n53 --- n63
    n53 --- n61
    n53 --- n60
    n53 --- n64
    n53 --- n66
    n53 --- n67
    n53 --- n65
    n53 --- n68
    n40 --- n56
    n40 --- n63
    n40 --- n53
    n40 --- n61
    n40 --- n60
    n40 --- n64
    n40 --- n66
    n40 --- n49
    n40 --- n67
    n40 --- n65
    n40 --- n68
    n25 --- n56
    n25 --- n63
    n25 --- n39
    n25 --- n53
    n25 --- n40
    n25 --- n30
    n25 --- n61
    n25 --- n60
    n25 --- n64
    n25 --- n66
    n25 --- n49
    n25 --- n31
    n25 --- n34
    n25 --- n67
    n25 --- n38
    n25 --- n36
    n25 --- n65
    n25 --- n68
    n25 --- n32
    n30 --- n56
    n30 --- n63
    n30 --- n39
    n30 --- n53
    n30 --- n40
    n30 --- n61
    n30 --- n60
    n30 --- n64
    n30 --- n66
    n30 --- n49
    n30 --- n31
    n30 --- n34
    n30 --- n67
    n30 --- n38
    n30 --- n36
    n30 --- n65
    n30 --- n68
    n30 --- n32
    n61 --- n63
    n61 --- n64
    n61 --- n66
    n61 --- n67
    n61 --- n65
    n61 --- n68
    n11 --- n56
    n11 --- n63
    n11 --- n39
    n11 --- n53
    n11 --- n40
    n11 --- n25
    n11 --- n30
    n11 --- n61
    n11 --- n60
    n11 --- n20
    n11 --- n19
    n11 --- n64
    n11 --- n66
    n11 --- n49
    n11 --- n31
    n11 --- n34
    n11 --- n67
    n11 --- n15
    n11 --- n38
    n11 --- n36
    n11 --- n65
    n11 --- n68
    n11 --- n32
    n60 --- n63
    n60 --- n61
    n60 --- n64
    n60 --- n66
    n60 --- n67
    n60 --- n65
    n60 --- n68
    n20 --- n56
    n20 --- n63
    n20 --- n39
    n20 --- n53
    n20 --- n40
    n20 --- n25
    n20 --- n30
    n20 --- n61
    n20 --- n60
    n20 --- n64
    n20 --- n66
    n20 --- n49
    n20 --- n31
    n20 --- n34
    n20 --- n67
    n20 --- n38
    n20 --- n36
    n20 --- n65
    n20 --- n68
    n20 --- n32
    n19 --- n56
    n19 --- n63
    n19 --- n39
    n19 --- n53
    n19 --- n40
    n19 --- n25
    n19 --- n30
    n19 --- n61
    n19 --- n60
    n19 --- n20
    n19 --- n64
    n19 --- n66
    n19 --- n49
    n19 --- n31
    n19 --- n34
    n19 --- n67
    n19 --- n38
    n19 --- n36
    n19 --- n65
    n19 --- n68
    n19 --- n32
    n4 --- n56
    n4 --- n63
    n4 --- n39
    n4 --- n7
    n4 --- n53
    n4 --- n40
    n4 --- n25
    n4 --- n30
    n4 --- n61
    n4 --- n11
    n4 --- n60
    n4 --- n20
    n4 --- n19
    n4 --- n64
    n4 --- n66
    n4 --- n49
    n4 --- n31
    n4 --- n34
    n4 --- n5
    n4 --- n67
    n4 --- n6
    n4 --- n15
    n4 --- n38
    n4 --- n36
    n4 --- n65
    n4 --- n68
    n4 --- n32
    n64 --- n66
    n64 --- n67
    n64 --- n65
    n64 --- n68
    n66 --- n67
    n66 --- n68
    n49 --- n56
    n49 --- n63
    n49 --- n53
    n49 --- n61
    n49 --- n60
    n49 --- n64
    n49 --- n66
    n49 --- n67
    n49 --- n65
    n49 --- n68
    n31 --- n56
    n31 --- n63
    n31 --- n39
    n31 --- n53
    n31 --- n40
    n31 --- n61
    n31 --- n60
    n31 --- n64
    n31 --- n66
    n31 --- n49
    n31 --- n34
    n31 --- n67
    n31 --- n38
    n31 --- n36
    n31 --- n65
    n31 --- n68
    n31 --- n32
    n0 --- n56
    n0 --- n63
    n0 --- n1
    n0 --- n39
    n0 --- n7
    n0 --- n53
    n0 --- n40
    n0 --- n25
    n0 --- n30
    n0 --- n61
    n0 --- n11
    n0 --- n60
    n0 --- n20
    n0 --- n19
    n0 --- n4
    n0 --- n64
    n0 --- n66
    n0 --- n49
    n0 --- n31
    n0 --- n34
    n0 --- n5
    n0 --- n67
    n0 --- n6
    n0 --- n15
    n0 --- n38
    n0 --- n36
    n0 --- n65
    n0 --- n68
    n0 --- n32
    n34 --- n56
    n34 --- n63
    n34 --- n39
    n34 --- n53
    n34 --- n40
    n34 --- n61
    n34 --- n60
    n34 --- n64
    n34 --- n66
    n34 --- n49
    n34 --- n67
    n34 --- n38
    n34 --- n36
    n34 --- n65
    n34 --- n68
    n5 --- n56
    n5 --- n63
    n5 --- n39
    n5 --- n7
    n5 --- n53
    n5 --- n40
    n5 --- n25
    n5 --- n30
    n5 --- n61
    n5 --- n11
    n5 --- n60
    n5 --- n20
    n5 --- n19
    n5 --- n64
    n5 --- n66
    n5 --- n49
    n5 --- n31
    n5 --- n34
    n5 --- n67
    n5 --- n6
    n5 --- n15
    n5 --- n38
    n5 --- n36
    n5 --- n65
    n5 --- n68
    n5 --- n32
    n67 --- n68
    n6 --- n56
    n6 --- n63
    n6 --- n39
    n6 --- n7
    n6 --- n53
    n6 --- n40
    n6 --- n25
    n6 --- n30
    n6 --- n61
    n6 --- n11
    n6 --- n60
    n6 --- n20
    n6 --- n19
    n6 --- n64
    n6 --- n66
    n6 --- n49
    n6 --- n31
    n6 --- n34
    n6 --- n67
    n6 --- n15
    n6 --- n38
    n6 --- n36
    n6 --- n65
    n6 --- n68
    n6 --- n32
    n15 --- n56
    n15 --- n63
    n15 --- n39
    n15 --- n53
    n15 --- n40
    n15 --- n25
    n15 --- n30
    n15 --- n61
    n15 --- n60
    n15 --- n20
    n15 --- n19
    n15 --- n64
    n15 --- n66
    n15 --- n49
    n15 --- n31
    n15 --- n34
    n15 --- n67
    n15 --- n38
    n15 --- n36
    n15 --- n65
    n15 --- n68
    n15 --- n32
    n38 --- n56
    n38 --- n63
    n38 --- n39
    n38 --- n53
    n38 --- n40
    n38 --- n61
    n38 --- n60
    n38 --- n64
    n38 --- n66
    n38 --- n49
    n38 --- n67
    n38 --- n65
    n38 --- n68
    n36 --- n56
    n36 --- n63
    n36 --- n39
    n36 --- n53
    n36 --- n40
    n36 --- n61
    n36 --- n60
    n36 --- n64
    n36 --- n66
    n36 --- n49
    n36 --- n67
    n36 --- n38
    n36 --- n65
    n36 --- n68
    n65 --- n66
    n65 --- n67
    n65 --- n68
    n32 --- n56
    n32 --- n63
    n32 --- n39
    n32 --- n53
    n32 --- n40
    n32 --- n61
    n32 --- n60
    n32 --- n64
    n32 --- n66
    n32 --- n49
    n32 --- n34
    n32 --- n67
    n32 --- n38
    n32 --- n36
    n32 --- n65
    n32 --- n68
```

## Top phrases by degree

| Rank | Phrase | Degree |
|---|---|---|
| 1 | `other companies` | 65 |
| 2 | `side project` | 65 |
| 3 | `Amazon` | 62 |
| 4 | `burned out` | 61 |
| 5 | `Duolingo` | 61 |
| 6 | `long hours` | 61 |
| 7 | `climber` | 61 |
| 8 | `Sam` | 60 |
| 9 | `Spanish` | 60 |
| 10 | `scraper` | 60 |
| 11 | `March` | 60 |
| 12 | `rock climbing` | 59 |
| 13 | `MountainProject.com` | 59 |
| 14 | `Mexico` | 57 |
| 15 | `Boston` | 57 |
| 16 | `software engineer` | 57 |
| 17 | `two months ago` | 57 |
| 18 | `fully remote work` | 57 |
| 19 | `Spanish practice` | 56 |
| 20 | `Alex` | 56 |
