"""Gazetteer matcher: find place mentions in a messy complaint and resolve them to a ward.

Scoring idea: rare words (Vijayanagar, Ashtalakshmi) count far more than common ones
(nagar, temple, bus, stn), using IDF over the gazetteer. A candidate span must explain
the gazetteer name AND the span must be explained by that name.
"""
import math, os
from collections import defaultdict
from dataclasses import dataclass, field
import pandas as pd
from rapidfuzz import fuzz, process
from src.geo.text_norm import tokens, skeleton

_FOLD = str.maketrans("dgbjcz", "tkpsss")   # Tamil has no voiced/unvoiced split: d~t, g~k, b~p
MAX_SPAN, MIN_SCORE, TOK_SIM, MAX_DISAMBIG_KM = 5, 0.60, 0.80, 3.0

def fold(t):
    return t.translate(_FOLD)

def haversine_km(a, b):
    (la1, lo1), (la2, lo2) = a, b
    p = math.pi / 180
    x = math.sin((la2 - la1) * p / 2) ** 2 + math.cos(la1 * p) * math.cos(la2 * p) * math.sin((lo2 - lo1) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(x))

@dataclass
class Match:
    span: str
    name: str
    kind: str            # landmark | area
    score: float
    rows: list = field(default_factory=list)   # [{ward_no, lat, lon}]
    spec: float = 0.0    # distinctiveness: score x total idf of the matched name

class GeoMatcher:
    def __init__(self, base="data/gazetteer", outside=("tambaram", "avadi")):
        lm = pd.read_csv(f"{base}/landmarks_clean.csv", encoding="utf-8-sig")
        ar = pd.read_csv(f"{base}/areas.csv", encoding="utf-8-sig")
        self.outside = [skeleton(o) for o in outside]
        self.forms = {}                       # id -> {toks, kind, name, rows}
        by_name = {}
        for kind, df in (("landmark", lm), ("area", ar)):
            for r in df.itertuples():
                key = (kind, skeleton(r.name))
                f = self.forms.setdefault(key, {"toks": [fold(t) for t in tokens(r.name)],
                                                "kind": kind, "name": r.name, "rows": []})
                f["rows"].append({"ward_no": int(r.ward_no), "lat": r.lat, "lon": r.lon})
                by_name.setdefault(r.name, key)
        self.unresolved_aliases = []
        if os.path.exists(f"{base}/aliases.csv"):
            al = pd.read_csv(f"{base}/aliases.csv", encoding="utf-8-sig")
            for a, c in zip(al["alias"], al["canonical"]):
                if c not in by_name:
                    self.unresolved_aliases.append(c); continue
                tgt = self.forms[by_name[c]]
                self.forms[("alias", skeleton(a), c)] = {"toks": [fold(t) for t in tokens(a)],
                    "kind": tgt["kind"], "name": c, "rows": tgt["rows"]}
        # 2-word names also get a joined variant: "Light House" <-> lighthouse, "T Nagar" <-> tnagar
        for fid, f in list(self.forms.items()):
            if len(f["toks"]) == 2:
                self.forms[fid + ("joined",)] = {**f, "toks": ["".join(f["toks"])]}
        df_count = defaultdict(int)
        self.inv = defaultdict(set)
        for fid, f in self.forms.items():
            for t in set(f["toks"]):
                df_count[t] += 1; self.inv[t].add(fid)
        n = len(self.forms)
        self.idf = {t: math.log(1 + n / c) for t, c in df_count.items()}
        self.idf_unk = max(self.idf.values())
        # very common words (nagar, temple, road, bus, stn ...) can never anchor a match on their own
        self.generic = {t for t, c in df_count.items() if c >= max(5, 0.015 * n)}
        self.vocab = list(self.idf)

    @staticmethod
    def _sim(q, v):
        if q == v: return 1.0
        if len(q) <= 3 or len(v) <= 3: return 0.0
        if q[0] != v[0]: return 0.0          # spelling variants rarely change the first letter
        s = fuzz.ratio(q, v) / 100
        return s if s >= TOK_SIM else 0.0

    def extract(self, text):
        toks = [fold(t) for t in tokens(text)]
        n = len(toks)
        sims = {}   # query token -> {vocab token: sim}
        for q in set(toks):
            sims[q] = {}
            for v, _, _ in process.extract(q, self.vocab, scorer=fuzz.ratio, score_cutoff=TOK_SIM * 100, limit=30):
                sv = self._sim(q, v)
                if sv: sims[q][v] = sv
            if q in self.idf: sims[q][q] = 1.0
        cands = []
        for i in range(n):
            for j in range(i + 1, min(n, i + MAX_SPAN) + 1):
                span = toks[i:j]
                fids = set()
                for s in span:
                    for v in sims[s]: fids |= self.inv[v]
                for fid in fids:
                    f = self.forms[fid]
                    wsum = sum(self.idf[t] for t in f["toks"])
                    cov_e = sum(self.idf[t] * max((sims[s].get(t, 0) for s in span), default=0) for t in f["toks"]) / wsum
                    num = den = 0.0
                    matched = []
                    for s in span:
                        best_t, best = max(((t, sims[s].get(t, 0)) for t in f["toks"]), key=lambda x: x[1], default=(None, 0))
                        if best > 0:
                            num += self.idf[best_t] * best; den += self.idf[best_t]; matched.append((s, best_t))
                        else: den += self.idf_unk
                    distinctive = [(s, t) for s, t in matched if t not in self.generic]
                    if not ((len(matched) >= 2 and distinctive) or any(len(s) >= 4 for s, _ in distinctive)):
                        continue            # no distinctive anchor word -> not a real place mention
                    score = cov_e * (num / den if den else 0)
                    if score >= MIN_SCORE:
                        rank = score + 0.10 * min(j - i - 1, 2) + 0.03 * (f["kind"] == "landmark")
                        cands.append((rank, score, i, j, fid))
        cands.sort(key=lambda c: -c[0])
        used, out = set(), []
        for _, score, i, j, fid in cands:
            if used & set(range(i, j)): continue
            used |= set(range(i, j))
            f = self.forms[fid]
            spec = score * sum(self.idf[t] for t in f["toks"])
            out.append(Match(" ".join(toks[i:j]), f["name"], f["kind"], round(score, 3), f["rows"], round(spec, 2)))
        return out

    def resolve(self, text):
        sk = skeleton(text)
        for o in self.outside:
            if o in sk:
                return {"ward_no": None, "confidence": 0.9, "how": "outside_gcc", "matches": [], "candidates": []}
        ms = self.extract(text)
        if not ms:
            return {"ward_no": None, "confidence": 0.0, "how": "no_location_found", "matches": [], "candidates": []}
        lms = [m for m in ms if m.kind == "landmark"]
        ars = [m for m in ms if m.kind == "area"]
        res = {"matches": ms, "candidates": []}
        if lms:
            top = max(x.score for x in lms)          # distinctiveness only breaks ties between near-equal matches
            m = max((x for x in lms if x.score >= top - 0.05), key=lambda x: x.spec)
            wards = sorted({r["ward_no"] for r in m.rows})
            if len(wards) == 1:
                return {**res, "ward_no": wards[0], "confidence": m.score, "how": "landmark"}
            ctx = ars[0] if ars else None
            same = self.forms.get(("area", skeleton(m.name)))      # e.g. landmark "Guindy" + area "Guindy"
            if same is not None:   # the name IS a locality: its own ward beats the nearest same-named landmark
                aw = sorted({r["ward_no"] for r in same["rows"]})
                return {**res, "ward_no": aw[0], "confidence": round(m.score * 0.6, 3),
                        "how": "area_same_name", "candidates": wards}
            if ctx is not None:   # disambiguate by distance to the named area
                a = (ctx.rows[0]["lat"], ctx.rows[0]["lon"])
                best = min(m.rows, key=lambda r: haversine_km(a, (r["lat"], r["lon"])))
                if haversine_km(a, (best["lat"], best["lon"])) <= MAX_DISAMBIG_KM:
                    return {**res, "ward_no": best["ward_no"], "confidence": round(m.score * 0.8, 3),
                            "how": "landmark_disambiguated_by_area", "candidates": wards}
            return {**res, "ward_no": None, "confidence": round(m.score * 0.5, 3),
                    "how": "ambiguous_landmark", "candidates": wards}
        a = ars[0]
        wards = sorted({r["ward_no"] for r in a.rows})
        return {**res, "ward_no": wards[0], "confidence": round(a.score * 0.6, 3),
                "how": "area_only_approx", "candidates": wards}
