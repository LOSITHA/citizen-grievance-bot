"""Translate-first: Tamil-script complaints -> English (IndicTrans2) -> baseline classifier.  python -m src.nlp.translate_first"""
import json, joblib, torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
try:
    from IndicTransToolkit.processor import IndicProcessor
except ImportError:
    from IndicTransToolkit import IndicProcessor
from src.nlp.evalutil import load, known_labels, report, misses, save_preds, TARGETS

CK = "ai4bharat/indictrans2-indic-en-dist-200M"
dev = "cuda" if torch.cuda.is_available() else "cpu"
rows, known = load("data/processed/indep_test.jsonl"), known_labels()
tok = AutoTokenizer.from_pretrained(CK, trust_remote_code=True)
mdl = AutoModelForSeq2SeqLM.from_pretrained(CK, trust_remote_code=True).to(dev).eval()
ip = IndicProcessor(inference=True)

def ta_to_en(sents):
    out = []
    for i in range(0, len(sents), 8):
        b = ip.preprocess_batch(sents[i:i+8], src_lang="tam_Taml", tgt_lang="eng_Latn")
        x = tok(b, truncation=True, padding="longest", max_length=256, return_tensors="pt").to(dev)
        with torch.no_grad():
            g = mdl.generate(**x, num_beams=5, max_length=256, use_cache=False)
        out += ip.postprocess_batch(tok.batch_decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=True), lang="eng_Latn")
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
md = report("Translate-first (IndicTrans2 for Tamil script only, then baseline)", rows, preds, known) + ["#### Misses", ""] + misses(rows, preds)
open("docs/results_translate.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
print("\n".join(md))
