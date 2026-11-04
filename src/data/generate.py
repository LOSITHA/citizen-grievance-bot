"""Synthetic complaint generator. Locations come from the gazetteer, so ward labels are free.

    python -m src.data.generate --n 4000 --seed 7

Train/val are split by PLACE (val places never appear in train) so the model must generalise to
unseen locations. The hand-written seed set stays the only test set.
"""
import argparse, hashlib, json, os, random, re
from collections import Counter
import pandas as pd
from src.geo.tamil_roman import has_tamil
from src.data.phrasebank import PROBLEMS, DUR, LOCPAT, OPEN, CLOSE

HONORIFICS = re.compile(r"^(Arulmigu|Arulmighu|Sri|Shri|Sree)\s+", re.I)
LANGS = ["en"] * 20 + ["ta"] * 15 + ["ta_rom"] * 25 + ["hi_rom"] * 15 + ["mixed"] * 25

def load_places(base="data/gazetteer"):
    lm = pd.read_csv(f"{base}/landmarks_clean.csv", encoding="utf-8-sig")
    ar = pd.read_csv(f"{base}/areas.csv", encoding="utf-8-sig")
    lm = lm[lm["name"].str.len() >= 5].copy()
    ar = ar[ar["name"].str.len() >= 4].copy()
    key = lm["name"].str.lower()
    lm["n_wards"] = key.map(lm.assign(k=key).groupby("k")["ward_no"].nunique())
    lm["ta"] = lm["name"].map(has_tamil)
    ar["ta"] = ar["name"].map(has_tamil)
    return lm, ar

def surface(name, lang, rng):
    if has_tamil(name):
        return name
    n = name
    if rng.random() < 0.4: n = HONORIFICS.sub("", n)
    if lang in ("ta_rom", "mixed", "hi_rom") and rng.random() < 0.4: n = re.sub(r"\bTemple\b", "koil", n)
    if rng.random() < 0.3: n = re.sub(r"\bBus (Terminus|Terminal|Stop|Station)\b", "bus stand", n, flags=re.I)
    return n

def pick_place(rng, lang, lm, ar, areas_by_ward):
    use_ta = lang == "ta" and rng.random() < 0.5
    lmp = lm[lm["ta"] == use_ta]; arp = ar[ar["ta"] == use_ta]
    if len(lmp) == 0: lmp = lm[~lm["ta"]]
    if len(arp) == 0: arp = ar[~ar["ta"]]
    if rng.random() < 0.7:
        r = lmp.iloc[rng.randrange(len(lmp))]
        name = surface(r["name"], lang, rng)
        if r["n_wards"] == 1:
            return dict(pieces=[(name, "LANDMARK")], ward=int(r["ward_no"]), kind="landmark", amb=False, cands=[], key=r["name"].lower())
        cands = sorted(int(w) for w in lm[lm["name"].str.lower() == r["name"].lower()]["ward_no"].unique())
        quals = areas_by_ward.get(int(r["ward_no"]), [])
        if quals and rng.random() < 0.7:
            q = surface(quals[rng.randrange(len(quals))], lang, rng)
            pieces = [(q, "AREA"), (" ", None), (name, "LANDMARK")] if rng.random() < 0.5 else [(name, "LANDMARK"), (", ", None), (q, "AREA")]
            return dict(pieces=pieces, ward=int(r["ward_no"]), kind="landmark_qualified", amb=False, cands=[], key=r["name"].lower())
        return dict(pieces=[(name, "LANDMARK")], ward=None, kind="ambiguous", amb=True, cands=cands, key=r["name"].lower())
    r = arp.iloc[rng.randrange(len(arp))]
    return dict(pieces=[(surface(r["name"], lang, rng), "AREA")], ward=int(r["ward_no"]), kind="area_approx", amb=False, cands=[], key=r["name"].lower())

def typo(word, rng):
    if len(word) < 5 or not word.isascii() or not word.isalpha(): return word
    i = rng.randrange(1, len(word) - 2)
    return word[:i] + word[i + 1] + word[i] + word[i + 2:]

def noisy(text, rng):
    if rng.random() < 0.3: text = text.lower()
    if rng.random() < 0.2:
        ws = text.split(" "); j = rng.randrange(len(ws)); ws[j] = typo(ws[j], rng); text = " ".join(ws)
    return text

def build(rng, prob, lang, place):
    if lang == "mixed":
        pl, patl, dl = "en", rng.choice(["ta_rom", "hi_rom"]), "en"
    else:
        pl = patl = dl = lang
    problem = rng.choice(prob[pl]).format(dur=rng.choice(DUR[dl]))
    opener = rng.choice(OPEN[patl if lang == "mixed" else lang]); closer = rng.choice(CLOSE[pl])
    pieces = [(opener, None)]
    if place is None:
        pieces += [(problem, None)]
    else:
        before, after = rng.choice(LOCPAT[patl]).split("{loc}")
        locp = [(before, None)] + place["pieces"] + [(after, None)]
        if patl == "en" and rng.random() < 0.5:
            pieces += [(problem + " ", None)] + locp
        elif patl == "en":
            pieces += locp + [(", " if rng.random() < 0.5 else " ", None), (problem, None)]
        else:
            pieces += locp + [(" ", None), (problem, None)]
    if closer.strip() and pl == "en":
        pieces += [(".", None)]        # full stop before an English closing phrase
    pieces += [(closer, None)]
    pieces = [(noisy(t, rng) if lab is None and t.strip() else t, lab) for t, lab in pieces]
    return "".join(t for t, _ in pieces).strip(), [{"text": t, "label": lab} for t, lab in pieces if lab]

def split_of(key):
    return "val" if int(hashlib.md5(key.encode()).hexdigest(), 16) % 100 < 15 else "train"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=4000); ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", default="data/processed/synth.jsonl")
    a = ap.parse_args()
    rng = random.Random(a.seed)
    lm, ar = load_places()
    areas_by_ward = ar[~ar["ta"]].groupby("ward_no")["name"].apply(list).to_dict()
    rows, seen = [], set()
    for _ in range(a.n * 30):
        if len(rows) >= a.n: break
        prob = PROBLEMS[rng.randrange(len(PROBLEMS))]
        lang = rng.choice(LANGS)
        place = pick_place(rng, lang, lm, ar, areas_by_ward) if rng.random() < 0.85 else None
        text, locs = build(rng, prob, lang, place)
        if text in seen: continue
        seen.add(text)
        rows.append({"id": f"s{len(rows):05d}", "text": text, "lang": lang, "dept": prob["dept"], "also": prob["also"],
                     "severity": prob["sev"], "urgency": prob["urg"], "locations": locs,
                     "ward_no": place["ward"] if place else None,
                     "ward_kind": place["kind"] if place else "none",
                     "ambiguous": place["amb"] if place else False,
                     "candidates": place["cands"] if place else [],
                     "split": split_of(place["key"]) if place else split_of(f"none{len(rows)}"),
                     "source": "synthetic"})
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} rows -> {a.out}")
    for k in ("dept", "severity", "urgency", "lang", "split", "ward_kind"):
        print(k, dict(Counter(r[k] for r in rows)))

if __name__ == "__main__":
    main()
