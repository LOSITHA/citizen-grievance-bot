"""Compare baseline / MuRIL / translate-first on the independent set.  python -m src.nlp.compare"""
import json
from src.nlp.evalutil import load, known_labels, hit, in_tax, TARGETS

rows, known = load("data/processed/indep_test.jsonl"), known_labels()
sysnames = {"baseline": "TF-IDF + LogReg", "muril": "MuRIL fine-tune", "translate": "Translate-first (ta only)"}
md = [f"# System comparison, independent test (n={len(rows)})", "",
      "| system | dept (all) | dept (in-taxonomy rows) | severity | urgency |", "|---|---|---|---|---|"]
bylang = {}
for k, name in sysnames.items():
    try: P = json.load(open(f"docs/preds_{k}.json", encoding="utf-8"))["preds"]
    except FileNotFoundError: continue
    acc = {t: sum(hit(r, t, p) for r, p in zip(rows, P[t])) / len(rows) for t in TARGETS}
    sub = [hit(r, "dept", p) for r, p in zip(rows, P["dept"]) if in_tax(r, "dept", known)]
    md.append(f"| {name} | {acc['dept']:.0%} | {sum(sub)/max(len(sub),1):.0%} ({sum(sub)}/{len(sub)}) | {acc['severity']:.0%} | {acc['urgency']:.0%} |")
    for lg in ("en", "ta", "ta_rom", "hi_rom"):
        v = [hit(r, "dept", p) for r, p in zip(rows, P["dept"]) if r["lang"] == lg]
        bylang.setdefault(lg, {})[name] = f"{sum(v)/len(v):.0%}"
md += ["", "## Department accuracy by language", "", "| lang | " + " | ".join(sysnames.values()) + " |", "|---|" + "---|" * len(sysnames)]
for lg, d in bylang.items(): md.append(f"| {lg} | " + " | ".join(d.get(n, "-") for n in sysnames.values()) + " |")
open("docs/results_comparison.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
print("\n".join(md))
