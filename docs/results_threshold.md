# Confidence threshold sweep (department, n=45)

Below the threshold a complaint goes to human triage instead of being auto-routed.

## baseline

| threshold | auto-routed | correct | misrouted | sent to triage | accuracy on auto-routed |
|---|---|---|---|---|---|
| 0.0 | 45 | 25 | 20 | 0 | 56% |
| 0.3 | 33 | 25 | 8 | 12 | 76% |
| 0.4 | 29 | 23 | 6 | 16 | 79% |
| 0.5 | 22 | 18 | 4 | 23 | 82% |
| 0.6 | 16 | 16 | 0 | 29 | 100% |
| 0.7 | 13 | 13 | 0 | 32 | 100% |
| 0.8 | 8 | 8 | 0 | 37 | 100% |
