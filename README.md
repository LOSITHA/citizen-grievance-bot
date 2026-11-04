# Multilingual Citizen Grievance Chatbot

**Topic:** HI-02 | **Author:** Lositha (solo)

An NLP chatbot that accepts grievances in regional Indian languages (Tamil, Hindi, English, and romanised Tanglish/Hinglish), routes each one to the right department, and tracks it until resolution.

## Status
- [x] Ward geo-matcher (boundary-aware, 150 m tolerance)
- [x] Synthetic training data + hand-written seed set
- [x] Baseline: TF-IDF + logistic regression (department / severity / urgency)
- [x] Independent test set: 45 hand-written complaints (English, Tamil script, Tanglish, Hinglish)
- [ ] MuRIL fine-tune vs baseline vs translate-first
- [ ] Confidence threshold + human-triage fallback
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