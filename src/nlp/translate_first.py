"""Translate-first: Tamil-script complaints -> English (NLLB-200) -> baseline classifier.  python -m src.nlp.translate_first"""
import json, joblib, torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from src.nlp.evalutil import load, known_labels, report, misses, save_preds, TARGETS

CK = "facebook/nllb-200-distilled-600M"
dev = "cuda" if torch.cuda.is_available() else "cpu"
rows, known = load("data/processed/indep_test.jsonl"), known_labels()
assert rows, "indep_test.jsonl is empty - git pull the latest repo first"
tok = AutoTokenizer.from_pretrained(CK, src_lang="tam_Taml")
mdl = AutoModelForSeq2SeqLM.from_pretrained(CK).to(dev).eval()
EN = tok.convert_tokens_to_ids("eng_Latn")

def ta_to_en(sents):
    out = []
    for i in range(0, len(sents), 8):
        x = tok(sents[i:i+8], return_tensors="pt", padding=True, truncation=True, max_length=256).to(dev)
        with torch.no_grad():
            g = mdl.generate(**x, forced_bos_token_id=EN, num_beams=4, max_length=256)
        out += tok.batch_decode(g, skip_special_tokens=True)
    return out

texts = [r["text"] for r in rows]
ta_idx = [i for i, r in enumerate(rows) if r["lang"] == "ta"]
for i, e in zip(ta_idx, ta_to_en([texts[i] for i in ta_idx])): texts[i] = e
json.dump({rows[i]["id"]: texts[i] for i in ta_idx}, open("docs/translations_ta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for i in ta_idx[:4]: print(rows[i]["id"], "->", texts[i])

models = joblib.load("models/baseline.joblib")
preds, conf = {}, {}
for t in TARGETS:
    P = models[t].predict_proba(texts)
    preds[t] = [models[t].classes_[j] for j in P.argmax(1)]; conf[t] = P.max(1).tolist()
save_preds("docs/preds_translate.json", rows, preds, conf)
md = report("Translate-first (NLLB-200 for Tamil script only, then baseline)", rows, preds, known) + ["#### Misses", ""] + misses(rows, preds)
open("docs/results_translate.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
print("\n".join(md))
