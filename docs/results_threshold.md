# Confidence threshold sweep (department, n=45)

Below the threshold a complaint goes to human triage instead of being auto-routed.

## baseline

| threshold | auto-routed | correct | misrouted | sent to triage | accuracy on auto-routed |
|---|---|---|---|---|---|
| 0.0 | 45 | 34 | 11 | 0 | 76% |
| 0.3 | 29 | 26 | 3 | 16 | 90% |
| 0.4 | 26 | 24 | 2 | 19 | 92% |
| 0.5 | 24 | 22 | 2 | 21 | 92% |
| 0.6 | 19 | 19 | 0 | 26 | 100% |
| 0.7 | 12 | 12 | 0 | 33 | 100% |
| 0.8 | 6 | 6 | 0 | 39 | 100% |

## muril

| threshold | auto-routed | correct | misrouted | sent to triage | accuracy on auto-routed |
|---|---|---|---|---|---|
| 0.0 | 45 | 22 | 23 | 0 | 49% |
| 0.3 | 0 | 0 | 0 | 45 | 0% |
| 0.4 | 0 | 0 | 0 | 45 | 0% |
| 0.5 | 0 | 0 | 0 | 45 | 0% |
| 0.6 | 0 | 0 | 0 | 45 | 0% |
| 0.7 | 0 | 0 | 0 | 45 | 0% |
| 0.8 | 0 | 0 | 0 | 45 | 0% |

## translate

| threshold | auto-routed | correct | misrouted | sent to triage | accuracy on auto-routed |
|---|---|---|---|---|---|
| 0.0 | 45 | 27 | 18 | 0 | 60% |
| 0.3 | 30 | 27 | 3 | 15 | 90% |
| 0.4 | 26 | 24 | 2 | 19 | 92% |
| 0.5 | 22 | 20 | 2 | 23 | 91% |
| 0.6 | 18 | 18 | 0 | 27 | 100% |
| 0.7 | 14 | 14 | 0 | 31 | 100% |
| 0.8 | 8 | 8 | 0 | 37 | 100% |
