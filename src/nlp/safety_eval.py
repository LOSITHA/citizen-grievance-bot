"""Does the safety override change severity/urgency accuracy on the independent set?  python -W ignore -m src.nlp.safety_eval"""
from src.nlp.evalutil import load
from src.app import pipeline as p

rows, M = load("data/processed/indep_test.jsonl"), p.MODELS
sb = sa = ub = ua = 0
flagged = []
for r in rows:
    sev = M["severity"].predict([r["text"]])[0]; urg = M["urgency"].predict([r["text"]])[0]
    s2, u2, f = p.safety_override(r["text"], sev, urg)
    sb += sev == r["severity"]; sa += s2 == r["severity"]; ub += urg == r["urgency"]; ua += u2 == r["urgency"]
    if f: flagged.append(f"{r['id']}: sev {sev}->{s2} (gold {r['severity']}), urg {urg}->{u2} (gold {r['urgency']})")
n = len(rows)
print(f"severity accuracy: {sb/n:.1%} -> {sa/n:.1%}")
print(f"urgency accuracy:  {ub/n:.1%} -> {ua/n:.1%}")
print(f"flagged {len(flagged)} complaints:"); print("\n".join(flagged))
