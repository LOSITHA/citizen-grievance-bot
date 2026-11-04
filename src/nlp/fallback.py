"""Confidence threshold sweep for department routing.  python -m src.nlp.fallback"""
import json
from src.nlp.evalutil import load, hit

rows = load("data/processed/indep_test.jsonl")
n = len(rows)
out = [f"# Confidence threshold sweep (department, n={n})", "",
       "Below the threshold a complaint goes to human triage instead of being auto-routed.", ""]
for name in ["baseline", "muril", "translate"]:
    try: P = json.load(open(f"docs/preds_{name}.json", encoding="utf-8"))
    except FileNotFoundError: continue
    pr, cf = P["preds"]["dept"], P["conf"]["dept"]
    out += [f"## {name}", "", "| threshold | auto-routed | correct | misrouted | sent to triage | accuracy on auto-routed |", "|---|---|---|---|---|---|"]
    for th in [0.0, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
        auto = [i for i in range(n) if cf[i] >= th]
        ok = sum(hit(rows[i], "dept", pr[i]) for i in auto)
        out.append(f"| {th:.1f} | {len(auto)} | {ok} | {len(auto) - ok} | {n - len(auto)} | {ok / max(len(auto), 1):.0%} |")
    out.append("")
open("docs/results_threshold.md", "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out))
