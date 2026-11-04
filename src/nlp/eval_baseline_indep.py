"""Score the saved baseline on the independent test set.  python -m src.nlp.eval_baseline_indep"""
import joblib
from src.nlp.evalutil import load, known_labels, report, misses, save_preds, TARGETS

rows, known = load("data/processed/indep_test.jsonl"), known_labels()
assert rows, "indep_test.jsonl is empty - re-run src/data/build_indep.py"
models = joblib.load("models/baseline.joblib")
preds, conf = {}, {}
for t in TARGETS:
    m = models[t]
    P = m.predict_proba([r["text"] for r in rows])
    preds[t] = [m.classes_[i] for i in P.argmax(1)]
    conf[t] = P.max(1).tolist()
save_preds("docs/preds_baseline.json", rows, preds, conf)
md = report(f"Baseline (TF-IDF + LogReg) on independent test, n={len(rows)}", rows, preds, known) + ["#### Misses", ""] + misses(rows, preds)
open("docs/results_baseline_indep.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
print("\n".join(md))

