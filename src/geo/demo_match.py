import json
from src.geo.matcher import GeoMatcher

gm = GeoMatcher()
if gm.unresolved_aliases:
    print("unresolved alias targets:", sorted(set(gm.unresolved_aliases)), "\n")
rows = [json.loads(l) for l in open("data/processed/seed_test.jsonl", encoding="utf-8-sig")]
for r in rows:
    res = gm.resolve(r["text"])
    names = [m.name for m in res["matches"]][:2]
    print(f'{r["id"]} ward={str(res["ward_no"]):5} conf={res["confidence"]:.2f} {res["how"]:31} {names}  <- {r["text"][:45]!r}')
