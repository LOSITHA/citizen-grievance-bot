# System comparison, independent test (n=45)

| system | dept (all) | dept (in-taxonomy rows) | severity | urgency |
|---|---|---|---|---|
| TF-IDF + LogReg | 56% | 76% (25/33) | 42% | 62% |
| MuRIL fine-tune | 49% | 67% (22/33) | 44% | 60% |
| Translate-first (ta only) | 60% | 82% (27/33) | 44% | 60% |

## Department accuracy by language

| lang | TF-IDF + LogReg | MuRIL fine-tune | Translate-first (ta only) |
|---|---|---|---|
| en | 67% | 50% | 67% |
| ta | 33% | 50% | 50% |
| ta_rom | 64% | 45% | 64% |
| hi_rom | 60% | 50% | 60% |
