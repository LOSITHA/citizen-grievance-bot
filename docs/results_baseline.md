# Baseline: TF-IDF (char 2-5 + word 1-2) + logistic regression

train n=3370 (synthetic) | synthetic val n=630 | hand-written test n=20

| target | synthetic val acc | synthetic val macro-F1 | TEST acc | TEST macro-F1 |
|---|---|---|---|---|
| dept | 100.0% | 1.000 | 100.0% (20/20) | 1.000 |
| severity | 100.0% | 1.000 | 80.0% (16/20) | 0.804 |
| urgency | 100.0% | 1.000 | 90.0% (18/20) | 0.808 |

## TEST accuracy by language style (department)

| lang | n | correct | acc |
|---|---|---|---|
| en | 6 | 6 | 100% |
| hi_rom | 4 | 4 | 100% |
| ta | 4 | 4 | 100% |
| ta_rom | 6 | 6 | 100% |

## TEST misses

| id | target | gold | predicted | text |
|---|---|---|---|---|
| g0012 | severity | high | medium | Garbage has not been collected on 5th Cross Street, Adambakk |
| g0015 | severity | medium | high | Mere ghar ke saamne ki road bahut kharab hai, Mylapore tank  |
| g0015 | urgency | routine | soon | Mere ghar ke saamne ki road bahut kharab hai, Mylapore tank  |
| g0018 | severity | medium | high | No water in the tap since morning, please check. |
| g0020 | severity | low | medium | Sir CMBT ke paas illegal parking aur footpath pe thele hain, |
| g0020 | urgency | routine | soon | Sir CMBT ke paas illegal parking aur footpath pe thele hain, |

_Synthetic val is near-ceiling by construction (templated text) - only the TEST columns mean anything._
