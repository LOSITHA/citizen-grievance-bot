"""First measurable result: do seed-complaint locations link to the gazetteer?"""
import json
import pandas as pd
from rapidfuzz import process, fuzz
from src.geo.text_norm import skeleton

lm = pd.read_csv("data/gazetteer/landmarks_clean.csv", encoding="utf-8-sig")
ar = pd.read_csv("data/gazetteer/areas.csv", encoding="utf-8-sig")
al = pd.read_csv("data/gazetteer/aliases.csv", encoding="utf-8-sig")

names = set(lm["name"]) | set(ar["name"])
bad = [c for c in al["canonical"] if c not in names]
if bad: print("ALIAS canonicals not found in gazetteer (fix spelling):", sorted(set(bad)), "\n")

cands = {}  # skeleton -> canonical name
for n in names: cands[skeleton(n)] = n
for a, c in zip(al["alias"], al["canonical"]): cands[skeleton(a)] = c
keys = list(cands)

rows = [json.loads(l) for l in open("data/processed/seed_test.jsonl", encoding="utf-8-sig")]
ok = total = 0
for r in rows:
    for loc in r["locations"]:
        if loc["label"] == "STREET": continue
        total += 1
        m = process.extractOne(skeleton(loc["text"]), keys, scorer=fuzz.ratio)
        hit = m and m[1] >= 80
        ok += bool(hit)
        print(f'{"OK " if hit else "MISS"} {loc["text"]!r:42} -> {cands[m[0]]!r} ({m[1]:.0f})')
print(f"\nlinked {ok}/{total}")
