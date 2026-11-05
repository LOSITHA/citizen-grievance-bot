# Uncertainty and paired tests (independent set, n=45)

## Accuracy with 95% bootstrap intervals

| system | measure | correct | accuracy | 95% interval |
|---|---|---|---|---|
| baseline v1 (8 depts) | department (all rows) | 25/45 | 55.6% | 42% to 69% |
| baseline v1 (8 depts) | department (labels seen in v2 training) | 25/42 | 59.5% | 45% to 74% |
| baseline v1 (8 depts) | severity | 19/45 | 42.2% | 29% to 58% |
| baseline v1 (8 depts) | urgency | 28/45 | 62.2% | 47% to 76% |
| baseline v2 (14 depts) | department (all rows) | 34/45 | 75.6% | 62% to 87% |
| baseline v2 (14 depts) | department (labels seen in v2 training) | 34/42 | 81.0% | 69% to 93% |
| baseline v2 (14 depts) | severity | 21/45 | 46.7% | 33% to 62% |
| baseline v2 (14 depts) | urgency | 30/45 | 66.7% | 53% to 80% |
| translate-first | department (all rows) | 27/45 | 60.0% | 44% to 76% |
| translate-first | department (labels seen in v2 training) | 27/42 | 64.3% | 50% to 79% |
| translate-first | severity | 20/45 | 44.4% | 31% to 60% |
| translate-first | urgency | 27/45 | 60.0% | 44% to 73% |
| MuRIL | department (all rows) | 22/45 | 48.9% | 33% to 62% |
| MuRIL | department (labels seen in v2 training) | 22/42 | 52.4% | 38% to 67% |
| MuRIL | severity | 20/45 | 44.4% | 31% to 58% |
| MuRIL | urgency | 27/45 | 60.0% | 47% to 73% |

## Severity and urgency as ordered labels

| system | target | exact | within one level | mean error (levels) | weighted kappa |
|---|---|---|---|---|---|
| baseline v1 (8 depts) | severity | 42% | 93% | 0.64 | 0.45 |
| baseline v1 (8 depts) | urgency | 62% | 91% | 0.47 | 0.23 |
| baseline v2 (14 depts) | severity | 47% | 91% | 0.62 | 0.39 |
| baseline v2 (14 depts) | urgency | 67% | 96% | 0.38 | 0.40 |
| translate-first | severity | 44% | 93% | 0.62 | 0.46 |
| translate-first | urgency | 60% | 93% | 0.47 | 0.25 |
| MuRIL | severity | 44% | 89% | 0.67 | 0.32 |
| MuRIL | urgency | 60% | 91% | 0.49 | 0.14 |

## Paired tests on department (exact McNemar)

| comparison | A right, B wrong | B right, A wrong | p-value |
|---|---|---|---|
| v1 (A) vs v2 (B), all rows | 0 | 9 | 0.004 |
| v1 (A) vs v2 (B), only rows whose gold department existed in v1 | 0 | 1 | 1.000 |
| v2 baseline (A) vs translate-first (B) | 9 | 2 | 0.065 |
| v2 baseline (A) vs MuRIL (B) | 15 | 3 | 0.008 |
