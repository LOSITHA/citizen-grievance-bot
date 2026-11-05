# System comparison, independent test (n=45)

| system | dept (all) | dept (in-taxonomy rows) | severity | urgency |
|---|---|---|---|---|
| TF-IDF + LogReg | 76% | 81% (34/42) | 47% | 67% |
| MuRIL fine-tune | 49% | 52% (22/42) | 44% | 60% |
| Translate-first (ta only) | 60% | 64% (27/42) | 44% | 60% |

## Department accuracy by language

| lang | TF-IDF + LogReg | MuRIL fine-tune | Translate-first (ta only) |
|---|---|---|---|
| en | 92% | 50% | 67% |
| ta | 58% | 50% | 50% |
| ta_rom | 73% | 45% | 64% |
| hi_rom | 80% | 50% | 60% |
