"""Fill gold_ward in seed_gold_wards.csv from independent coordinates (seed_gold_coords.csv).

Independent = the coordinates come from a source other than the matcher, so agreement is evidence.
Rows are flagged CHECK when the point is < 150 m from a ward boundary or disagrees with the prediction.
Locality-only complaints (kind=area) are marked 'soft': a locality spans several wards.
"""
import csv, re
import geopandas as gpd
from shapely.geometry import Point
from src.geo.ward_lookup import WardLookup

GOLD = "data/processed/seed_gold_wards.csv"
COORDS = "data/processed/seed_gold_coords.csv"
NUM = re.compile(r"[-+]?\d+(?:\.\d+)?")
FRAGILE_M = 150

wl = WardLookup()

def parse_latlon(s):
    nums = [float(x) for x in NUM.findall(s)][:2]      # handles "13.05, 80.21" and "13.05° N, 80.21° E"
    return tuple(nums) if len(nums) == 2 else None

def locate(la, lo):
    pt = gpd.GeoSeries([Point(lo, la)], crs=4326).to_crs(epsg=32644).iloc[0]
    hits = wl.sindex.query(pt, predicate="intersects")
    if len(hits):
        g = wl.proj.geometry.iloc[hits[0]]
        return int(wl.proj.iloc[hits[0]]["ward_no"]), g.boundary.distance(pt)
    return None, None

coords = {r["id"]: r for r in csv.DictReader(open(COORDS, encoding="utf-8-sig"))}
rows = list(csv.DictReader(open(GOLD, encoding="utf-8-sig")))
fields = ["id", "text", "predicted_ward", "how", "latlon", "gold_ward", "gold_kind", "gold_margin_m", "gold_check", "gold_note"]
for r in rows:
    c = coords.get(r["id"], {})
    r["gold_kind"] = c.get("kind", "")
    r["gold_margin_m"] = r.get("gold_margin_m") or ""      # survive reruns
    r["gold_check"] = r.get("gold_check") or ""
    special = (c.get("special") or "").strip().upper()
    ll = (r.get("latlon") or "").strip() or (c.get("latlon") or "").strip()
    if (r.get("gold_ward") or "").strip():
        pass                                              # already filled (by an earlier run or by you): keep it
    elif special:
        r["gold_ward"] = special
    elif ll and parse_latlon(ll):
        r["latlon"] = ll
        ward, margin = locate(*parse_latlon(ll))
        r["gold_ward"] = str(ward) if ward is not None else "OUTSIDE"
        r["gold_margin_m"] = "" if margin is None else f"{margin:.0f}"
        if r["gold_kind"] == "area":
            r["gold_check"] = "soft"
        elif margin is None or margin < FRAGILE_M or str(ward) != str(r.get("predicted_ward") or ""):
            r["gold_check"] = "CHECK"
    note = (r.get("gold_note") or "").strip()
    if c.get("note") and c["note"] not in note:             # do not re-append on reruns
        note = (note + " " + c["note"]).strip()
    r["gold_note"] = note
with open(GOLD, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"filled. empty gold_ward: {sum(1 for r in rows if not (r['gold_ward'] or '').strip())}")
print("CHECK (verify on Google Maps):", [r["id"] for r in rows if r["gold_check"] == "CHECK"])
print("soft (locality-only):", [r["id"] for r in rows if r["gold_check"] == "soft"])
