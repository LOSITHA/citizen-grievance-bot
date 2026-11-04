import json
from collections import defaultdict
from sklearn.metrics import f1_score

TARGETS = ["dept", "severity", "urgency"]

def load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8-sig") if l.strip()]

def known_labels(path="data/processed/synth.jsonl"):
    k = {t: set() for t in TARGETS}
    for r in load(path):
        for t in TARGETS: k[t].add(r[t])
    return k

def ok_set(r): return r.get("dept_ok") or [r["dept"]]
def hit(r, t, p): return p in ok_set(r) if t == "dept" else p == r[t]
def in_tax(r, t, known):
    return any(d in known["dept"] for d in ok_set(r)) if t == "dept" else r[t] in known[t]

def report(name, rows, preds, known):
    L = [f"### {name}", "", "| target | acc (all rows) | acc (gold label exists in training labels) | macro-F1 |", "|---|---|---|---|"]
    for t in TARGETS:
        ok = [hit(r, t, p) for r, p in zip(rows, preds[t])]
        sub = [o for o, r in zip(ok, rows) if in_tax(r, t, known)]
        gold = [p if o else (r["dept"] if t == "dept" else r[t]) for r, p, o in zip(rows, preds[t], ok)]
        f1 = f1_score(gold, preds[t], average="macro", zero_division=0)
        L.append(f"| {t} | {sum(ok)/len(ok):.1%} ({sum(ok)}/{len(ok)}) | {sum(sub)/max(len(sub),1):.1%} ({sum(sub)}/{len(sub)}) | {f1:.3f} |")
    L += ["", "| lang | n | dept correct | dept acc |", "|---|---|---|---|"]
    by = defaultdict(list)
    for r, p in zip(rows, preds["dept"]): by[r["lang"]].append(hit(r, "dept", p))
    for l, v in sorted(by.items()): L.append(f"| {l} | {len(v)} | {sum(v)} | {sum(v)/len(v):.0%} |")
    return L + [""]

def misses(rows, preds, n=60):
    L = ["| id | target | gold | predicted | text |", "|---|---|---|---|---|"]
    for i, r in enumerate(rows):
        for t in TARGETS:
            if not hit(r, t, preds[t][i]):
                g = " / ".join(ok_set(r)) if t == "dept" else r[t]
                L.append(f"| {r.get('id', i)} | {t} | {g} | {preds[t][i]} | {r['text'][:n].replace('|', '/')} |")
    return L

def save_preds(path, rows, preds, conf):
    ids = [r.get("id", i) for i, r in enumerate(rows)]
    json.dump({"ids": ids, "preds": preds, "conf": conf}, open(path, "w", encoding="utf-8"), ensure_ascii=False)
