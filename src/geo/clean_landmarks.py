"""landmarks.csv -> landmarks_clean.csv (fix types, drop generic names, add ambiguity count)."""
import re
import pandas as pd
from src.geo.text_norm import skeleton

GENERIC = {"temple", "church", "masjid", "mosque", "school", "hospital", "clinic",
           "park", "police station", "bus stop", "market"}

def fix_type(name, t):
    n = name.lower()
    if re.search(r"bus (terminus|terminal|stand|stop|station)|\bcmbt\b", n): return "bus_stop"
    if "market" in n: return "marketplace"
    if re.search(r"temple|koil|kovil|church|masjid|mosque|dargah|mandir", n): return "worship"
    if re.search(r"hospital|clinic|nursing home", n): return "hospital"
    if "police" in n: return "police"
    return t

df = pd.read_csv("data/gazetteer/landmarks.csv", encoding="utf-8-sig")
df["name"] = df["name"].str.strip().str.replace(r"\s+", " ", regex=True)
df = df[~df["name"].str.lower().isin(GENERIC)].copy()
df["type"] = [fix_type(n, t) for n, t in zip(df["name"], df["type"])]
df["key"] = df["name"].map(skeleton)
df = df.drop_duplicates(subset=["key", "ward_no"])
df["n_wards_same_name"] = df["key"].map(df.groupby("key")["ward_no"].nunique())
df.to_csv("data/gazetteer/landmarks_clean.csv", index=False, encoding="utf-8-sig")
print(len(df), "clean landmarks")
print("ambiguous names (appear in >1 ward):", (df.drop_duplicates("key")["n_wards_same_name"] > 1).sum())
print(df.sort_values("n_wards_same_name", ascending=False).drop_duplicates("key")
        [["name", "n_wards_same_name"]].head(8).to_string(index=False))
