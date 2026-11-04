# Multilingual Citizen Grievance Chatbot

**Topic:** HI-02 | **Author:** Lositha (solo)

An NLP chatbot that accepts grievances in regional Indian languages (Tamil, Hindi, English, and romanised Tanglish/Hinglish), routes each one to the right department, and tracks it until resolution.

## Status
- [x] Ward geo-matcher (boundary-aware, 150 m tolerance)
- [x] Synthetic training data + hand-written seed set
- [x] Baseline: TF-IDF + logistic regression (department / severity / urgency)
- [x] Independent test set: 45 hand-written complaints (English, Tamil script, Tanglish, Hinglish)
- [ ] MuRIL fine-tune vs baseline vs translate-first
- [x] Confidence threshold + human-triage fallback
- [ ] Ticket tracking with SLA timers and auto-escalation
- [ ] Chat interface + officer console
- [ ] Final evaluation, demo, report

## Evaluation honesty
- Synthetic validation data is templated, so it is near 100% by construction. Only hand-written test sets are reported.
- Gold wards are partly circular (same polygons as the matcher). Locations within ~150 m of a ward boundary accept either ward.
- Some test complaints belong to departments that the training data never contained. These are reported separately.

## Reproduce
- Ward matcher: `python -m src.geo.eval_matcher`
- Baseline: `python -m src.nlp.baseline` (results in `docs/results_baseline.md`)

## Layout
`src/geo` ward matching | `src/nlp` models and evaluation | `src/app` pipeline, tracker, UI | `data/processed` datasets | `docs` results
# citizen-grievance-bot
## Results (independent test: 45 hand-written complaints)

| system | dept (all 45) | dept (33 rows whose label exists in training) | Tamil-script dept | severity | urgency |
|---|---|---|---|---|---|
| TF-IDF + LogReg baseline | 55.6% | 75.8% | 33% (4/12) | 42.2% | 62.2% |
| Translate-first (NLLB-200 for Tamil script, then baseline) | 60.0% | 81.8% | 50% (6/12) | 44.4% | 60.0% |

Key findings:
- Synthetic validation is ~100% because the text is templated; on hand-written complaints department accuracy drops to ~56%. Only the hand-written numbers are meaningful.
- Tamil script is the weakest input. Translating to English first lifted it from 4/12 to 6/12 correct. The sample is small, so this is suggestive, not proven.
- 12 of the 45 complaints belong to departments absent from the training data (revenue, police, education, food and civil supplies, parks). Without a safeguard these are confidently misrouted.

### Confidence threshold and human triage (baseline, department)

| threshold | auto-routed | misrouted | sent to human triage |
|---|---|---|---|
| 0.0 | 45 | 20 | 0 |
| 0.5 | 22 | 4 | 23 |
| 0.6 | 16 | 0 | 29 |
| 0.8 | 8 | 0 | 37 |

The demo auto-routes at confidence >= 0.5 and sends the rest to a human triage queue with a clarifying question in the user's language. This operating point was chosen by looking at the same 45 rows, so treat it as illustrative, not tuned.

## Limitations
- The test set is small (n=45); one row is about 2.2 percentage points.
- Severity and urgency are subjective labels and are the hardest targets (42-62%).
- Training data is synthetic; real citizen text is messier.
- Translate-first covers Tamil script only; romanised Tanglish and Hinglish are not translated.
- The ward matcher is evaluated separately (`python -m src.geo.eval_matcher`) but is not yet wired into the chat flow.

