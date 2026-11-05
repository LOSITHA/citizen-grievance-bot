"""Bootstrap intervals, ordinal metrics and paired tests on the independent set.  python -W ignore -m src.nlp.stats"""
import json, random
from math import comb
from sklearn.metrics import cohen_kappa_score
from src.nlp.evalutil import load, hit, in_tax, known_labels

rows = load("data/processed/indep_test.jsonl")
n, ids = len(rows), [r["id"] for r in rows]
known2, known1 = known_labels(), known_labels("data/processed/synth.jsonl")
ORD = {"severity": ["low", "medium", "high", "critical"], "urgency": ["routine", "soon", "immediate"]}
SYS = {"baseline v1 (8 depts)": "docs/preds_baseline_v1.json", "baseline v2 (14 depts)": "docs/preds_baseline.json",
       "translate-first": "docs/preds_translate.json", "MuRIL": "docs/preds_muril.json"}
random.seed(0)

P = {}
for name, path in SYS.items():
    try: d = json.load(open(path, encoding="utf-8"))
    except FileNotFoundError: continue
    if d["ids"] != ids: print("skipping (row order differs):", name); continue
    P[name] = d["preds"]
if not P: raise SystemExit("no prediction files found in docs/")

def boot(v, B=2000):
    m = sorted(sum(random.choices(v, k=len(v))) / len(v) for _ in range(B))
    return m[int(0.025 * B)], m[int(0.975 * B)]

def mcnemar(a, b):
    x = sum(1 for i, j in zip(a, b) if i and not j); y = sum(1 for i, j in zip(a, b) if j and not i)
    m = x + y
    if m == 0: return x, y, 1.0
    return x, y, min(1.0, 2 * sum(comb(m, k) for k in range(min(x, y) + 1)) / 2 ** m)

md = [f"# Uncertainty and paired tests (independent set, n={n})", "",
      "## Accuracy with 95% bootstrap intervals", "", "| system | measure | correct | accuracy | 95% interval |", "|---|---|---|---|---|"]
H = {}
for name, pr in P.items():
    dept = [int(hit(r, "dept", p)) for r, p in zip(rows, pr["dept"])]
    H[name] = dept
    sets = [("department (all rows)", dept),
            ("department (labels seen in v2 training)", [h for h, r in zip(dept, rows) if in_tax(r, "dept", known2)]),
            ("severity", [int(hit(r, "severity", p)) for r, p in zip(rows, pr["severity"])]),
            ("urgency", [int(hit(r, "urgency", p)) for r, p in zip(rows, pr["urgency"])])]
    for label, v in sets:
        lo, hi = boot(v)
        md.append(f"| {name} | {label} | {sum(v)}/{len(v)} | {sum(v)/len(v):.1%} | {lo:.0%} to {hi:.0%} |")

md += ["", "## Severity and urgency as ordered labels", "",
       "| system | target | exact | within one level | mean error (levels) | weighted kappa |", "|---|---|---|---|---|---|"]
for name, pr in P.items():
    for t, L in ORD.items():
        idx = {l: i for i, l in enumerate(L)}
        g = [idx[r[t]] for r in rows]; p = [idx[x] for x in pr[t]]
        kap = cohen_kappa_score(g, p, weights="quadratic", labels=list(range(len(L))))
        md.append(f"| {name} | {t} | {sum(a == b for a, b in zip(g, p))/n:.0%} | {sum(abs(a - b) <= 1 for a, b in zip(g, p))/n:.0%} | "
                  f"{sum(abs(a - b) for a, b in zip(g, p))/n:.2f} | {kap:.2f} |")

md += ["", "## Paired tests on department (exact McNemar)", "", "| comparison | A right, B wrong | B right, A wrong | p-value |", "|---|---|---|---|"]
def pair(label, a, b, mask=None):
    mask = mask or [True] * n
    x, y, p = mcnemar([h for h, m in zip(H[a], mask) if m], [h for h, m in zip(H[b], mask) if m])
    md.append(f"| {label} | {x} | {y} | {p:.3f} |")
A, v1 = "baseline v2 (14 depts)", "baseline v1 (8 depts)"
if v1 in H and A in H:
    pair("v1 (A) vs v2 (B), all rows", v1, A)
    pair("v1 (A) vs v2 (B), only rows whose gold department existed in v1", v1, A, [in_tax(r, "dept", known1) for r in rows])
for other in ["translate-first", "MuRIL"]:
    if other in H and A in H: pair(f"v2 baseline (A) vs {other} (B)", A, other)

open("docs/results_stats.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
print("\n".join(md))
