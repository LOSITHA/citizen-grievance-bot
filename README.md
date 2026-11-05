# Multilingual Citizen Grievance Chatbot

**Topic: HI-02** | Solo project by Lositha

A chatbot that accepts citizen complaints written in English, Tamil script, Tanglish (romanised Tamil) and Hinglish (romanised Hindi), routes each one to the right department, gives the citizen a ticket number, and tracks the complaint until it is resolved or escalated.

## What it does
- **Understands code-mixed complaints** directly (Tanglish and Hinglish), without translating first.
- **Routes to a department** and predicts **severity** and **urgency** (TF-IDF + logistic regression).
- **Knows when it is unsure.** Below a confidence threshold the complaint goes to a human triage queue and the bot asks a clarifying question in the citizen's language instead of guessing.
- **Ticket numbers** (GRV-000001 and so on) with a ticket card: department, priority, status, expected resolution time.
- **Tracking.** Citizens type their ticket number in the chat or open the Track my complaint tab: progress bar, latest message from the department, timeline.
- **Officer console.** Summary cards, filterable queue, status updates with a message to the citizen, one-click escalation of overdue tickets.
- **SLA timers and auto-escalation** driven by severity and urgency.
- **Duplicate linking.** Similar open complaints in the same department are linked to one parent ticket, which shows hotspots.
- **Explainable routing.** The top text features behind each decision are stored on the ticket.
- **Safety override.** Life-risk wording (live wire, open manhole, dog bite, ambulance delay) forces at least high severity and immediate urgency.
- **Small talk handled.** Greetings, thanks and one-word messages do not create junk tickets.

## How a complaint flows

    citizen message
          |
          v
    small-talk filter (hi / thanks / one word) --> friendly reply, no ticket
          |
          v
    language detection (en / ta / ta_rom / hi_rom)
          |
          v
    classifier: department + severity + urgency + confidence
          |
          v
    safety override (life-risk words -> at least high, immediate)
          |
          +-- confidence below threshold --> "Needs Triage" ticket + clarifying question
          |
          v
    duplicate check --> new ticket (SQLite) with an SLA due time
          |
          v
    reply in the citizen's language + ticket card
          |
          v
    Track tab / officer console: Routed -> In progress -> Resolved, or Escalated if the SLA is missed

## Results
All numbers are on an independent test set of 45 hand-written complaints (12 English, 12 Tamil script, 11 Tanglish, 10 Hinglish). Synthetic validation data is templated and scores about 100%, so it is not reported as evidence.

### How the classifier improved

| model | extra training data | department (all 45) | department (labels it knows) | Tamil script | severity | urgency |
|---|---|---|---|---|---|---|
| 1. Baseline | none | 55.6% (25/45) | 75.8% (25/33) | 33% (4/12) | 42.2% | 62.2% |
| 2. + six new departments | 1,800 rows | 71.1% (32/45) | 76.2% (32/42) | 58% (7/12) | 48.9% | 68.9% |
| 3. + neutral-wording augmentation (current) | 1,267 rows | **75.6% (34/45)** | **81.0% (34/42)** | 58% (7/12) | 46.7% | 66.7% |

Current model, department accuracy by language: English 92% (11/12), Hinglish 80% (8/10), Tanglish 73% (8/11), Tamil script 58% (7/12).

The first six departments added (revenue, police, education, food and civil supplies, parks, animal control) came from error analysis: 12 of the 45 test complaints belonged to departments the first model had never seen. Accuracy on departments the model already knew barely changed (75.8% to 76.2%), so the headline gain is mostly taxonomy coverage, not better classification.

### Alternatives (trained on the original data, not yet re-run on the larger data)

| system | department (all 45) | department (labels it knows) | Tamil script | severity | urgency |
|---|---|---|---|---|---|
| TF-IDF + LogReg (original data) | 55.6% | 75.8% | 33% | 42.2% | 62.2% |
| Translate-first (NLLB-200 for Tamil script, then classifier) | 60.0% (27/45) | 81.8% (27/33) | 50% (6/12) | 44.4% | 60.0% |
| MuRIL fine-tune | 49% (22/45) | 67% (22/33) | 50% (6/12) | 44% | 60% |

Translating Tamil first helped Tamil (4/12 to 6/12). MuRIL did not beat the simple baseline. Its confidence never exceeded 0.3 on any test complaint, so it could not be used with the triage threshold; it is probably undertrained on small, templated data.

### Confidence threshold and human triage (current model, department)

| threshold | auto-routed | correct | misrouted | sent to triage | accuracy on auto-routed |
|---|---|---|---|---|---|
| 0.0 | 45 | 34 | 11 | 0 | 76% |
| 0.3 | 29 | 26 | 3 | 16 | 90% |
| 0.4 | 26 | 24 | 2 | 19 | 92% |
| **0.5 (used in the app)** | 24 | 22 | 2 | 21 | 92% |
| 0.6 | 19 | 19 | 0 | 26 | 100% |
| 0.7 | 12 | 12 | 0 | 33 | 100% |
| 0.8 | 6 | 6 | 0 | 39 | 100% |

The app uses 0.5 as an operating point (it automates about half the complaints and sends the shaky ones to a human). It was chosen by looking at this same sweep, so treat it as illustrative.

### Other checks
- 20 hand-written seed complaints: department 20/20, severity 16/20, urgency 18/20.
- Safety override, measured on the first model: severity 42.2% to 44.4%, urgency 62.2% to 64.4% (6 complaints flagged). The keywords were chosen knowing the test complaints, so this is a design choice, not independent evidence.
- Smoke tests: `python -m tests.smoke_test` (3 tests).

## Limitations
- The test set is small (n=45); one complaint is about 2.2 percentage points, so differences of a few points are within noise.
- The 45 complaints are no longer fully untouched: the department list and the wording of the training data were adjusted after seeing which test complaints failed. A fresh held-out set is future work.
- Severity and urgency are subjective labels and are the hardest targets (47% and 67%).
- Training data is synthetic and templated; real citizen text is messier.
- Tamil script is the weakest input (58%). Translate-first covers Tamil script only.
- Hindi in Devanagari script is recognised for greetings and replies, but the classifier is trained and evaluated on romanised Hindi (Hinglish) only.
- The ward matcher (`src/geo`) is evaluated separately and is not wired into the chat flow.

## Run it
1. `git clone https://github.com/LOSITHA/citizen-grievance-bot.git` and `cd citizen-grievance-bot`
2. `python -m venv .venv`, activate it, then `pip install -r requirements.txt`
3. `python -m src.app.ui` and open http://127.0.0.1:7860
4. Optional: set `SLA_SCALE` to a small number (for example `0.001`) before launching to see SLA escalation in seconds.
5. Checks: `python -m tests.smoke_test`

The trained model is committed (`models/baseline.joblib`). Tickets are stored in `data/tracker.db`, created on first run.

## Repository layout
- `src/geo/` ward matching
- `src/data/` test-set builder (`build_indep.py`) and extra training data generator (`gen_extra.py`)
- `src/nlp/` baseline, evaluation, MuRIL, translate-first, threshold sweep, comparison
- `src/app/` pipeline, ticket tracker, views, Gradio UI, demo-input picker
- `tests/` smoke tests
- `data/processed/` datasets (`synth_v2.jsonl` is the training data, `indep_test.jsonl` the independent test set)
- `docs/` result tables and demo inputs

## Reproduce the experiments
- Training data: `python src/data/gen_extra.py`
- Test set: `python src/data/build_indep.py`
- Baseline: `python -m src.nlp.baseline`, then `python -m src.nlp.eval_baseline_indep`
- Threshold sweep: `python -m src.nlp.fallback`
- System comparison: `python -m src.nlp.compare`
- Safety override: `python -m src.nlp.safety_eval`
- MuRIL and translate-first need a GPU or Colab: `python -m src.nlp.train_muril`, `python -m src.nlp.translate_first`

## AI assistance
Built with help from Claude (Anthropic) for code and design discussion. The 45-complaint test set and its labels were written by the author. See `docs/ai_tools_used.md`.

## Future work
- Write a fresh held-out test set after freezing the system, for one unbiased number.
- Re-run MuRIL and translate-first on the larger training data, and train MuRIL longer.
- Calibrate the confidence scores before choosing the triage threshold.
- Wire the ward matcher into the chat flow for ward-aware duplicates and hotspot counts.
- Add Devanagari Hindi training data.
