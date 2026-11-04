@'

"""Convert the 45 hand-written complaints (markdown tables) to indep\_test.jsonl and audit labels vs synth.jsonl.

&#x20;   python src/data/build\_indep.py

"""

import json, re



SRC, OUT, SYNTH = "data/raw/indep\_test\_source.md", "data/processed/indep\_test.jsonl", "data/processed/synth.jsonl"

\# Rename your department names to the names used in synth.jsonl. Edit AFTER you see the audit, then re-run.

DEPT\_MAP = {"Electricity Board": "Electricity"}



def lang\_of(n):

&#x20;   return "en" if n <= 12 else "ta" if n <= 24 else "ta\_rom" if n <= 35 else "hi\_rom"



known = {t: set() for t in ("dept", "severity", "urgency")}

for l in open(SYNTH, encoding="utf-8-sig"):

&#x20;   r = json.loads(l)

&#x20;   for t in known: known\[t].add(r\[t])



def canon(v, t):

&#x20;   low = {k.lower(): k for k in known\[t]}

&#x20;   return low.get(v.strip().lower(), v.strip())



rows = \[]

for line in open(SRC, encoding="utf-8-sig"):

&#x20;   if not re.match(r"^\\|\\s\*C\\d+\\s\*\\|", line): continue

&#x20;   cid, text, dept, sev, urg = \[c.strip() for c in line.strip().strip("|").split("|")]\[:5]

&#x20;   alts = \[]

&#x20;   for d in re.split(r"\\s\*/\\s\*", dept):

&#x20;       d = "Unclassified" if d.startswith("Unclassified") else DEPT\_MAP.get(d, d)

&#x20;       alts.append(canon(d, "dept"))

&#x20;   rows.append({"id": cid, "text": text, "lang": lang\_of(int(cid\[1:])), "dept": alts\[0], "dept\_ok": alts,

&#x20;                "severity": canon(sev, "severity"), "urgency": canon(urg, "urgency"), "split": "indep"})



with open(OUT, "w", encoding="utf-8") as f:

&#x20;   for r in rows: f.write(json.dumps(r, ensure\_ascii=False) + "\\n")

print(f"wrote {len(rows)} rows -> {OUT}")

for lg in ("en", "ta", "ta\_rom", "hi\_rom"): print(f"  {lg}: {sum(r\['lang'] == lg for r in rows)}")

print("Labels NOT in synth.jsonl (the baseline can never predict these):")

for t in known:

&#x20;   vals = sorted({v for r in rows for v in (r\["dept\_ok"] if t == "dept" else \[r\[t]]) if v not in known\[t]})

&#x20;   print(f"  {t}: {vals}")

'@ | Set-Content -Encoding utf8 src\\data\\build\_indep.py

python src\\data\\build\_indep.py

