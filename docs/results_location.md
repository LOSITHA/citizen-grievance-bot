# Location matcher results (seed set)

| Subset | n | correct | wrong | abstain | accuracy |
|---|---|---|---|---|---|
| trusted | 17 | 17 | 0 | 0 | 100% |
| unverified | 0 | - | - | - | - |
| locality | 3 | 2 | 1 | 0 | 67% |
| all rows | 20 | 19 | 1 | 0 | 95% |

## By resolution type (trusted rows)

| how | n | correct | wrong | abstain | accuracy |
|---|---|---|---|---|---|
| landmark | 14 | 14 | 0 | 0 | 100% |
| no_location_found | 2 | 2 | 0 | 0 | 100% |
| outside_gcc | 1 | 1 | 0 | 0 | 100% |

## Human-fallback threshold (trusted rows with a true ward)

A ward is auto-routed only if confidence >= cutoff; otherwise a human decides.

| cutoff | auto-routed | accuracy of auto-routed | coverage |
|---|---|---|---|
| 0.0 | 14 | 14/14 | 100% |
| 0.5 | 14 | 14/14 | 100% |
| 0.6 | 14 | 14/14 | 100% |
| 0.7 | 14 | 14/14 | 100% |
| 0.8 | 14 | 14/14 | 100% |
| 0.9 | 13 | 13/13 | 93% |
| 1.0 | 12 | 12/12 | 86% |

## Matcher MIN_SCORE sweep (trusted rows, strict accuracy)

| MIN_SCORE | correct | wrong | abstain |
|---|---|---|---|
| 0.5 | 16 | 1 | 0 |
| 0.6 | 17 | 0 | 0 |
| 0.7 | 17 | 0 | 0 |
| 0.8 | 17 | 0 | 0 |

## Not correct (inspect these)

| id | bucket | gold | predicted | how | matches |
|---|---|---|---|---|---|
| g0012 | locality | 163 | 165 | landmark (wrong) | ['Adambakkam'] |

_n=20 seed complaints: small sample, treat as a sanity check, not a benchmark._
