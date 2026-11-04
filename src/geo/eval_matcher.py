"""Evaluate the location matcher against data/processed/seed_gold_wards.csv.

Row buckets:  trusted    = gold_check empty or 'verified' (and the special OUTSIDE / NONE rows)
              unverified = gold_check 'CHECK'  (two independent sources disagree or point is near a boundary)
              locality   = gold_check 'soft'   (complaint only names a locality; no single true ward)
"""
import csv, os
import src.geo.matcher as M

GOLD = "data/processed/seed_gold_wards.csv"
OUT = "docs/results_location.md"

def judge(gold, res):
    g = gold.strip().upper()
    if g == "OUTSIDE": return "correct" if res["how"] == "outside_gcc" else "wrong"
    if g == "NONE":    return "correct" if res["how"] == "no_location_found" else "wrong"
    if res["ward_no"] is None: return "abstain"
    return "correct" if str(res["ward_no"]) in g.split("|") else "wrong"   # "a|b" = either ward is acceptable

def bucket(r):
    return {"CHECK": "unverified", "soft": "locality"}.get((r.get("gold_check") or "").strip(), "trusted")

def evaluate(rows, gm):
    return [(r, res := gm.resolve(r["text"]), judge(r["gold_ward"], res)) for r in rows]

def line(name, items):
    n = len(items); c = sum(j == "correct" for *_, j in items)
    w = sum(j == "wrong" for *_, j in items); a = sum(j == "abstain" for *_, j in items)
    return f"| {name} | {n} | {c} | {w} | {a} | {c / n:.0%} |" if n else f"| {name} | 0 | - | - | - | - |"

def main():
    rows = list(csv.DictReader(open(GOLD, encoding="utf-8-sig")))
    gm = M.GeoMatcher()
    items = evaluate(rows, gm)
    md = ["# Location matcher results (seed set)", "",
          "| Subset | n | correct | wrong | abstain | accuracy |", "|---|---|---|---|---|---|"]
    for b in ("trusted", "unverified", "locality"):
        md.append(line(b, [x for x in items if bucket(x[0]) == b]))
    md.append(line("all rows", items))
    md += ["", "## By resolution type (trusted rows)", "",
           "| how | n | correct | wrong | abstain | accuracy |", "|---|---|---|---|---|---|"]
    tr = [x for x in items if bucket(x[0]) == "trusted"]
    for how in sorted({x[1]["how"] for x in tr}):
        md.append(line(how, [x for x in tr if x[1]["how"] == how]))

    ward_rows = [x for x in tr if x[0]["gold_ward"].strip().upper() not in ("OUTSIDE", "NONE")]
    md += ["", "## Human-fallback threshold (trusted rows with a true ward)", "",
           "A ward is auto-routed only if confidence >= cutoff; otherwise a human decides.", "",
           "| cutoff | auto-routed | accuracy of auto-routed | coverage |", "|---|---|---|---|"]
    for cut in (0.0, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        auto = [x for x in ward_rows if x[1]["ward_no"] is not None and x[1]["confidence"] >= cut]
        ok = sum(x[2] == "correct" for x in auto)
        md.append(f"| {cut:.1f} | {len(auto)} | {ok}/{len(auto)} | {len(auto) / max(1, len(ward_rows)):.0%} |"
                  if auto else f"| {cut:.1f} | 0 | - | 0% |")

    md += ["", "## Matcher MIN_SCORE sweep (trusted rows, strict accuracy)", "", "| MIN_SCORE | correct | wrong | abstain |", "|---|---|---|---|"]
    keep = M.MIN_SCORE
    for v in (0.5, 0.6, 0.7, 0.8):
        M.MIN_SCORE = v
        t = [x for x in evaluate([r for r, *_ in tr], gm)]
        md.append(f"| {v:.1f} | {sum(j == 'correct' for *_, j in t)} | {sum(j == 'wrong' for *_, j in t)} | {sum(j == 'abstain' for *_, j in t)} |")
    M.MIN_SCORE = keep

    wrong = [x for x in items if x[2] != "correct"]
    md += ["", "## Not correct (inspect these)", "", "| id | bucket | gold | predicted | how | matches |", "|---|---|---|---|---|---|"]
    for r, res, j in wrong:
        md.append(f"| {r['id']} | {bucket(r)} | {r['gold_ward']} | {res['ward_no']} | {res['how']} ({j}) | {[m.name for m in res['matches']][:2]} |")
    md += ["", f"_n={len(items)} seed complaints: small sample, treat as a sanity check, not a benchmark._"]
    os.makedirs("docs", exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("\n".join(md))

if __name__ == "__main__":
    main()
