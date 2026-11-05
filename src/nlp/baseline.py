"""TF-IDF + logistic regression baseline for department, severity and urgency.

Train on synthetic 'train', report on synthetic 'val' (sanity only) and on the hand-written seed set (the real test).
    python -m src.nlp.baseline
"""
import json, os
from collections import defaultdict
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import make_pipeline, make_union

TARGETS = ["dept", "severity", "urgency"]
SYNTH, TEST = "data/processed/synth_v2.jsonl", "data/processed/seed_test.jsonl"

def load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8-sig")]

def make_model():
    feats = make_union(
        TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), sublinear_tf=True, min_df=2),
        TfidfVectorizer(analyzer="word", ngram_range=(1, 2), sublinear_tf=True,
                        token_pattern=r"[^\s,.;:!?()\[\]\"']+"))   # keeps Tamil combining marks intact
    return make_pipeline(feats, LogisticRegression(max_iter=3000, C=5.0, class_weight="balanced"))

def score(model, rows, t):
    y = [r[t] for r in rows]; p = model.predict([r["text"] for r in rows])
    return accuracy_score(y, p), f1_score(y, p, average="macro"), list(p)

def main():
    synth, test = load(SYNTH), load(TEST)
    tr = [r for r in synth if r["split"] == "train"]; va = [r for r in synth if r["split"] == "val"]
    md = ["# Baseline: TF-IDF (char 2-5 + word 1-2) + logistic regression", "",
          f"train n={len(tr)} (synthetic) | synthetic val n={len(va)} | hand-written test n={len(test)}", "",
          "| target | synthetic val acc | synthetic val macro-F1 | TEST acc | TEST macro-F1 |", "|---|---|---|---|---|"]
    models, test_preds = {}, {}
    for t in TARGETS:
        m = make_model().fit([r["text"] for r in tr], [r[t] for r in tr])
        va_a, va_f, _ = score(m, va, t); te_a, te_f, p = score(m, test, t)
        models[t], test_preds[t] = m, p
        md.append(f"| {t} | {va_a:.1%} | {va_f:.3f} | {te_a:.1%} ({sum(a == r[t] for a, r in zip(p, test))}/{len(test)}) | {te_f:.3f} |")
    md += ["", "## TEST accuracy by language style (department)", "", "| lang | n | correct | acc |", "|---|---|---|---|"]
    by = defaultdict(list)
    for r, p in zip(test, test_preds["dept"]): by[r["lang"]].append(p == r["dept"])
    for l, v in sorted(by.items()): md.append(f"| {l} | {len(v)} | {sum(v)} | {sum(v) / len(v):.0%} |")
    md += ["", "## TEST misses", "", "| id | target | gold | predicted | text |", "|---|---|---|---|---|"]
    for i, r in enumerate(test):
        for t in TARGETS:
            if test_preds[t][i] != r[t]:
                md.append(f"| {r['id']} | {t} | {r[t]} | {test_preds[t][i]} | {r['text'][:60]} |")
    md += ["", "_Synthetic val is near-ceiling by construction (templated text) - only the TEST columns mean anything._"]
    os.makedirs("models", exist_ok=True); os.makedirs("docs", exist_ok=True)
    joblib.dump(models, "models/baseline.joblib", compress=3)
    open("docs/results_baseline.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("\n".join(md))
    print(f"\nmodel size: {os.path.getsize('models/baseline.joblib') / 1e6:.1f} MB")

if __name__ == "__main__":
    main()
