# Confidence threshold sweep (department, n=45)

Below the threshold a complaint goes to human triage instead of being auto-routed.

## baseline

| threshold | auto-routed | correct | misrouted | sent to triage | accuracy on auto-routed |
|---|---|---|---|---|---|
| 0.0 | 45 | 32 | 13 | 0 | 71% |
| 0.3 | 30 | 26 | 4 | 15 | 87% |
| 0.4 | 25 | 23 | 2 | 20 | 92% |
| 0.5 | 23 | 22 | 1 | 22 | 96% |
| 0.6 | 18 | 18 | 0 | 27 | 100% |
| 0.7 | 9 | 9 | 0 | 36 | 100% |
| 0.8 | 4 | 4 | 0 | 41 | 100% |

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
