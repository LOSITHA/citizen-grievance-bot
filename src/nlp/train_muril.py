"""Multi-task MuRIL fine-tune (dept / severity / urgency). Run in Colab:  python -m src.nlp.train_muril"""
import time, random
import numpy as np, torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer, AutoModel, get_linear_schedule_with_warmup
from src.nlp.evalutil import load, known_labels, report, misses, save_preds, TARGETS

MODEL, EPOCHS, BS, LR, MAXLEN, SEED = "google/muril-base-cased", 4, 32, 3e-5, 96, 42
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
dev = "cuda" if torch.cuda.is_available() else "cpu"

synth = load("data/processed/synth.jsonl")
train = [r for r in synth if r["split"] == "train"]
val = [r for r in synth if r["split"] == "val"]
seeds, indep, known = load("data/processed/seed_test.jsonl"), load("data/processed/indep_test.jsonl"), known_labels()
classes = {t: sorted(known[t]) for t in TARGETS}
c2i = {t: {c: i for i, c in enumerate(classes[t])} for t in TARGETS}
tok = AutoTokenizer.from_pretrained(MODEL)

class DS(Dataset):
    def __init__(s, rows): s.rows = rows
    def __len__(s): return len(s.rows)
    def __getitem__(s, i): return s.rows[i]

def enc_of(b): return tok([r["text"] for r in b], padding=True, truncation=True, max_length=MAXLEN, return_tensors="pt")
def collate_train(b): return enc_of(b), {t: torch.tensor([c2i[t][r[t]] for r in b]) for t in TARGETS}

class MT(nn.Module):
    def __init__(s):
        super().__init__()
        s.enc = AutoModel.from_pretrained(MODEL)
        h = s.enc.config.hidden_size
        s.drop = nn.Dropout(0.1)
        s.heads = nn.ModuleDict({t: nn.Linear(h, len(classes[t])) for t in TARGETS})
    def forward(s, ids, mask):
        x = s.drop(s.enc(input_ids=ids, attention_mask=mask).last_hidden_state[:, 0])
        return {t: s.heads[t](x) for t in TARGETS}

model = MT().to(dev)
opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=0.01)
dl = DataLoader(DS(train), batch_size=BS, shuffle=True, collate_fn=collate_train)
sch = get_linear_schedule_with_warmup(opt, int(0.1 * EPOCHS * len(dl)), EPOCHS * len(dl))
ce = nn.CrossEntropyLoss()
print(f"device={dev} train={len(train)} val={len(val)} seeds={len(seeds)} indep={len(indep)}")
for ep in range(EPOCHS):
    model.train(); t0 = time.time(); run = 0
    for enc, y in dl:
        enc = {k: v.to(dev) for k, v in enc.items()}
        out = model(enc["input_ids"], enc["attention_mask"])
        loss = sum(ce(out[t], y[t].to(dev)) for t in TARGETS)
        loss.backward(); nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step(); sch.step(); opt.zero_grad(); run += loss.item()
    print(f"epoch {ep+1}/{EPOCHS} loss {run/len(dl):.4f} ({time.time()-t0:.0f}s)")

@torch.no_grad()
def predict(rows):
    model.eval(); preds = {t: [] for t in TARGETS}; conf = {t: [] for t in TARGETS}
    for b in DataLoader(DS(rows), batch_size=64, collate_fn=lambda b: enc_of(b)):
        b = {k: v.to(dev) for k, v in b.items()}
        out = model(b["input_ids"], b["attention_mask"])
        for t in TARGETS:
            c, i = out[t].softmax(-1).max(-1)
            preds[t] += [classes[t][j] for j in i.tolist()]; conf[t] += c.tolist()
    return preds, conf

md = ["# MuRIL multi-task fine-tune", ""]
for name, rows in [("synthetic val (sanity only)", val), ("seed test (20)", seeds), ("independent test (45)", indep)]:
    p, c = predict(rows)
    md += report(name, rows, p, known)
    if rows is indep:
        save_preds("docs/preds_muril.json", rows, p, c)
        md += ["#### Misses (independent)", ""] + misses(rows, p)
open("docs/results_muril.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
print("\n".join(md))
torch.save(model.state_dict(), "models/muril_mt.pt")
