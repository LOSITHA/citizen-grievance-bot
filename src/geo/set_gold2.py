import pandas as pd
p = "data/processed/seed_gold_wards.csv"
df = pd.read_csv(p, dtype=str, encoding="utf-8-sig").fillna("")
def setg(i, ward, note):
    m = df["id"] == i
    df.loc[m, ["gold_ward", "gold_check"]] = [ward, "verified"]
    df.loc[m, "gold_note"] = note
setg("g0010", "179", "Google Maps point 12.9926,80.2704 -> ward 179 (54 m from coast); matches OSM node")
setg("g0017", "71|74", "Perambur railway station 13.1077,80.2448 -> ward 71, only 18 m from ward 74 boundary")
df.to_csv(p, index=False, encoding="utf-8-sig")
print(df[["id", "predicted_ward", "gold_ward", "gold_check"]].to_string(index=False))
