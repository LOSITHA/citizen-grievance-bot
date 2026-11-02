"""Fetch Chennai locality names from OSM -> data/gazetteer/areas.csv"""
import json, os, requests
import pandas as pd
from src.geo.ward_lookup import WardLookup
from src.geo.build_landmarks import MIRRORS, HEADERS, BBOX

Q = f"""[out:json][timeout:90];
node["place"~"^(suburb|neighbourhood|quarter|village|town|locality)$"]["name"]({BBOX});
out center tags;"""
RAW, OUT = "data/gazetteer/osm_areas_raw.json", "data/gazetteer/areas.csv"

def fetch():
    for url in MIRRORS:
        try:
            r = requests.post(url, data={"data": Q}, headers=HEADERS, timeout=120)
            r.raise_for_status(); return r.json()
        except Exception as e:
            print("failed:", url, e)
    raise SystemExit("all mirrors failed")

data = json.load(open(RAW, encoding="utf-8")) if os.path.exists(RAW) else fetch()
json.dump(data, open(RAW, "w", encoding="utf-8"), ensure_ascii=False)
wl, rows = WardLookup(), []
for e in data["elements"]:
    t = e["tags"]; ward, how = wl.ward_of(e["lat"], e["lon"], return_how=True)
    if ward is None: continue
    rows.append({"name": t["name"], "name_ta": t.get("name:ta", ""), "lat": e["lat"],
                 "lon": e["lon"], "ward_no": ward, "ward_how": how})
df = pd.DataFrame(rows).drop_duplicates("name")
df.to_csv(OUT, index=False, encoding="utf-8-sig")
print(len(df), "areas ->", OUT)
