"""Convert the 45 hand-written complaints (markdown tables) to indep_test.jsonl and audit labels vs synth.jsonl.
    python src/data/build_indep.py
"""
import json, re

SRC, OUT, SYNTH = "data/raw/indep_test_source.md", "data/processed/indep_test.jsonl", "data/processed/synth.jsonl"
# Rename your department names to the names used in synth.jsonl. Edit AFTER you see the audit, then re-run.
DEPT_MAP = {"Electricity Board": "Electricity"}

def lang_of(n):
    return "en" if n <= 12 else "ta" if n <= 24 else "ta_rom" if n <= 35 else "hi_rom"

known = {t: set() for t in ("dept", "severity", "urgency")}
for l in open(SYNTH, encoding="utf-8-sig"):
    r = json.loads(l)
    for t in known: known[t].add(r[t])

def canon(v, t):
    low = {k.lower(): k for k in known[t]}
    return low.get(v.strip().lower(), v.strip())

rows = []
for line in open(SRC, encoding="utf-8-sig"):
    if not re.match(r"^\|\s*C\d+\s*\|", line): continue
    cid, text, dept, sev, urg = [c.strip() for c in line.strip().strip("|").split("|")][:5]
    alts = []
    for d in re.split(r"\s*/\s*", dept):
        d = "Unclassified" if d.startswith("Unclassified") else DEPT_MAP.get(d, d)
        alts.append(canon(d, "dept"))
    rows.append({"id": cid, "text": text, "lang": lang_of(int(cid[1:])), "dept": alts[0], "dept_ok": alts,
                 "severity": canon(sev, "severity"), "urgency": canon(urg, "urgency"), "split": "indep"})

with open(OUT, "w", encoding="utf-8") as f:
    for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(f"wrote {len(rows)} rows -> {OUT}")
for lg in ("en", "ta", "ta_rom", "hi_rom"): print(f"  {lg}: {sum(r['lang'] == lg for r in rows)}")
print("Labels NOT in synth.jsonl (the baseline can never predict these):")
for t in known:
    vals = sorted({v for r in rows for v in (r["dept_ok"] if t == "dept" else [r[t]]) if v not in known[t]})
    print(f"  {t}: {vals}")
