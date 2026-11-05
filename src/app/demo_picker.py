"""Pick demo inputs that route correctly AND confidently.  python -W ignore -m src.app.demo_picker"""
import sys
from src.nlp.evalutil import load
from src.app import pipeline as p

try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

NEW = {"revenue", "police", "education", "food_civil_supplies", "parks", "animal_control"}
EXTRA = [
    ("en", "The ration shop has been closed all week and we cannot collect our rice", "food_civil_supplies"),
    ("en", "The police are refusing to register an FIR for my stolen bike", "police"),
    ("en", "The government school has no maths teacher and exams are near", "education"),
    ("en", "My patta transfer has been pending at the taluk office for months", "revenue"),
    ("en", "The children's play equipment in the park is broken and rusted", "parks"),
    ("ta_rom", "Ration kadai romba naal moodiye irukku, arisi vaanga mudiyala", "food_civil_supplies"),
    ("hi_rom", "School mein maths ke teacher nahi hain aur exam paas hain", "education"),
    ("ta", "பூங்காவில் விளக்குகள் எரியவில்லை, மாலையில் நடக்க முடியவில்லை", "parks"),
]
M = p.MODELS
rows = [dict(r) for r in load("data/processed/indep_test.jsonl")]
for i, (lang, text, gold) in enumerate(EXTRA, 1):
    rows.append({"id": f"X{i}", "text": text, "lang": lang, "dept_ok": [gold], "dept": gold, "own": True})

C = []
for r in rows:
    P = M["dept"].predict_proba([r["text"]])[0]; k = int(P.argmax()); pred = M["dept"].classes_[k]
    sev = M["severity"].predict([r["text"]])[0]; urg = M["urgency"].predict([r["text"]])[0]
    gold = r.get("dept_ok") or [r["dept"]]
    C.append({**r, "pred": pred, "conf": float(P[k]), "ok": pred in gold, "auto": float(P[k]) >= p.THRESH,
              "flag": p.safety_override(r["text"], sev, urg)[2], "gold": gold})

good = sorted([c for c in C if c["ok"] and c["auto"]], key=lambda c: -c["conf"])
def pick(f, n=2): return [c for c in good if f(c)][:n]
slots = [
    ("1. Tanglish complaint", pick(lambda c: c["lang"] == "ta_rom" and not c.get("own"))),
    ("2. Tamil-script complaint", pick(lambda c: c["lang"] == "ta" and not c.get("own"))),
    ("3. Hinglish complaint", pick(lambda c: c["lang"] == "hi_rom" and not c.get("own"))),
    ("4. English complaint", pick(lambda c: c["lang"] == "en" and not c.get("own"))),
    ("5. Life-risk wording (safety override)", pick(lambda c: c["flag"])),
    ("6. A newly added department", pick(lambda c: set(c["gold"]) & NEW)),
    ("7. Vague complaint (goes to human triage)", [c for c in C if "Unclassified" in c["gold"] and not c["auto"]][:2]),
]
out = [f"Threshold in use: {p.THRESH}. Correct AND auto-routed: {len(good)} of {len(C)} candidates.", ""]
for title, items in slots:
    out.append("## " + title)
    if not items: out.append("(no candidate met the criteria for this slot)")
    for c in items:
        tag = " [my own sentence]" if c.get("own") else ""
        out.append(f"[{c['id']}] ({c['lang']}) routes to {c['pred']}, confidence {c['conf']:.2f}{' SAFETY' if c['flag'] else ''}{tag}")
        out.append(c["text"])
    out.append("")
open("docs/demo_inputs.txt", "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out))
