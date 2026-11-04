# Location matcher results (seed set)

| Subset | n | correct | wrong | abstain | accuracy |
|---|---|---|---|---|---|
| trusted | 15 | 15 | 0 | 0 | 100% |
| unverified | 2 | 0 | 2 | 0 | 0% |
| locality | 3 | 2 | 1 | 0 | 67% |
| all rows | 20 | 17 | 3 | 0 | 85% |

## By resolution type (trusted rows)

| how | n | correct | wrong | abstain | accuracy |
|---|---|---|---|---|---|
| landmark | 12 | 12 | 0 | 0 | 100% |
| no_location_found | 2 | 2 | 0 | 0 | 100% |
| outside_gcc | 1 | 1 | 0 | 0 | 100% |

## Human-fallback threshold (trusted rows with a true ward)

A ward is auto-routed only if confidence >= cutoff; otherwise a human decides.

| cutoff | auto-routed | accuracy of auto-routed | coverage |
|---|---|---|---|
| 0.0 | 12 | 12/12 | 100% |
| 0.5 | 12 | 12/12 | 100% |
| 0.6 | 12 | 12/12 | 100% |
| 0.7 | 12 | 12/12 | 100% |
| 0.8 | 12 | 12/12 | 100% |
| 0.9 | 11 | 11/11 | 92% |
| 1.0 | 10 | 10/10 | 83% |

## Matcher MIN_SCORE sweep (trusted rows, strict accuracy)

| MIN_SCORE | correct | wrong | abstain |
|---|---|---|---|
| 0.5 | 14 | 1 | 0 |
| 0.6 | 15 | 0 | 0 |
| 0.7 | 15 | 0 | 0 |
| 0.8 | 15 | 0 | 0 |

## Not correct (inspect these)

| id | bucket | gold | predicted | how | matches |
|---|---|---|---|---|---|
| g0010 | unverified | 174 | 179 | landmark (wrong) | ['Besant Nagar', 'Ashtalakshmi Temple'] |
| g0012 | locality | 163 | 165 | landmark (wrong) | ['Adambakkam'] |
| g0017 | unverified | 44 | 71 | landmark (wrong) | ['Perambur Railway Station', 'SITE'] |

_n=20 seed complaints: small sample, treat as a sanity check, not a benchmark._
