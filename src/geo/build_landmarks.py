"""Fetch Chennai landmarks from OpenStreetMap (Overpass) -> data/gazetteer/landmarks.csv"""
import json, os, time, requests
import pandas as pd
from src.geo.ward_lookup import WardLookup

BBOX = "12.83,80.05,13.30,80.35"  # south,west,north,east (covers GCC + margin)
MIRRORS = ["https://overpass-api.de/api/interpreter",
           "https://overpass.kumi.systems/api/interpreter",
           "https://overpass.private.coffee/api/interpreter"]
QUERY = f"""
[out:json][timeout:120];
(
  nwr["amenity"="place_of_worship"]["name"]({BBOX});
  nwr["amenity"="bus_station"]["name"]({BBOX});
  nwr["highway"="bus_stop"]["name"]({BBOX});
  nwr["amenity"="hospital"]["name"]({BBOX});
  nwr["amenity"="school"]["name"]({BBOX});
  nwr["amenity"="marketplace"]["name"]({BBOX});
  nwr["railway"="station"]["name"]({BBOX});
  nwr["amenity"="police"]["name"]({BBOX});
  nwr["leisure"="park"]["name"]({BBOX});
  nwr["tourism"="attraction"]["name"]({BBOX});
);
out center tags;
"""
HEADERS = {"User-Agent": "citizen-grievance-bot/0.1 (student project, VIT Chennai)", "Accept": "*/*"}
RAW = "data/gazetteer/osm_raw.json"
OUT = "data/gazetteer/landmarks.csv"

def kind(t):
    if t.get("amenity") == "place_of_worship": return "worship"
    if t.get("amenity") == "bus_station" or t.get("highway") == "bus_stop": return "bus_stop"
    if t.get("railway") == "station": return "railway_station"
    for k in ("hospital", "school", "marketplace", "police"):
        if t.get("amenity") == k: return k
    if t.get("leisure") == "park": return "park"
    return "attraction"

def fetch():
    for url in MIRRORS:
        try:
            print("trying", url)
            r = requests.post(url, data={"data": QUERY}, headers=HEADERS, timeout=180)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print("failed:", e); time.sleep(3)
    raise SystemExit("All Overpass mirrors failed (network blocked?). Tell Claude.")

def main():
    data = json.load(open(RAW, encoding="utf-8")) if os.path.exists(RAW) else fetch()
    json.dump(data, open(RAW, "w", encoding="utf-8"), ensure_ascii=False)
    wl = WardLookup()
    rows = []
    for e in data["elements"]:
        t = e.get("tags", {})
        lat = e.get("lat") or e.get("center", {}).get("lat")
        lon = e.get("lon") or e.get("center", {}).get("lon")
        if lat is None: continue
        ward, how = wl.ward_of(lat, lon, return_how=True)
        if ward is None: continue  # outside GCC
        rows.append({"osm_id": f'{e["type"]}/{e["id"]}', "name": t["name"],
                     "name_ta": t.get("name:ta", ""), "type": kind(t),
                     "lat": round(lat, 6), "lon": round(lon, 6),
                     "ward_no": ward, "ward_how": how})
    df = pd.DataFrame(rows).drop_duplicates(subset=["name", "ward_no", "type"])
    df.to_csv(OUT, index=False, encoding="utf-8-sig")
    print(f"{len(df)} landmarks in GCC -> {OUT}")
    print(df["type"].value_counts().to_string())
    print("wards covered:", df["ward_no"].nunique(), "/ 200")

if __name__ == "__main__":
    main()
