import csv, json, os
from src.geo.matcher import GeoMatcher

OUT = "data/processed/seed_gold_wards.csv"
if os.path.exists(OUT):
    raise SystemExit(f"{OUT} already exists - delete it first if you really want a fresh template")
gm = GeoMatcher()
rows = [json.loads(l) for l in open("data/processed/seed_test.jsonl", encoding="utf-8-sig")]
with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["id", "text", "predicted_ward", "how", "latlon", "gold_ward", "gold_note"])
    for r in rows:
        res = gm.resolve(r["text"])
        w.writerow([r["id"], r["text"], res["ward_no"] or "", res["how"], "", "", ""])
print("wrote", OUT)
