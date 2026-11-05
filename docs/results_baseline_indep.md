### Baseline (TF-IDF + LogReg) on independent test, n=45

| target | acc (all rows) | acc (gold label exists in training labels) | macro-F1 |
|---|---|---|---|
| dept | 71.1% (32/45) | 76.2% (32/42) | 0.654 |
| severity | 48.9% (22/45) | 48.9% (22/45) | 0.539 |
| urgency | 68.9% (31/45) | 68.9% (31/45) | 0.626 |

| lang | n | dept correct | dept acc |
|---|---|---|---|
| en | 12 | 9 | 75% |
| hi_rom | 10 | 8 | 80% |
| ta | 12 | 7 | 58% |
| ta_rom | 11 | 8 | 73% |

#### Misses

| id | target | gold | predicted | text |
|---|---|---|---|---|
| C02 | severity | medium | high | The garbage collection vehicle has not visited our area for  |
| C03 | dept | roads | animal_control | A large pothole has developed near the main junction. Two-wh |
| C06 | severity | high | medium | There is a strong sewage smell coming from the drainage line |
| C07 | dept | public_health | police | A government hospital has been turning away patients because |
| C07 | severity | high | medium | A government hospital has been turning away patients because |
| C08 | urgency | soon | routine | My ration card details are incorrect, and the shopkeeper ref |
| C10 | severity | medium | low | Buses on our route are frequently cancelled without any prio |
| C10 | urgency | soon | routine | Buses on our route are frequently cancelled without any prio |
| C11 | severity | low | medium | I have been trying to get my property tax receipt corrected, |
| C12 | dept | parks | police | There is something wrong with the public park near our stree |
| C12 | severity | low | high | There is something wrong with the public park near our stree |
| C12 | urgency | routine | soon | There is something wrong with the public park near our stree |
| C14 | dept | solid_waste | police | தெருவில் குப்பைகள் அள்ளப்படாமல் குவிந்து கிடக்கின்றன. இதனால் |
| C15 | dept | roads | police | எங்கள் தெருவில் உள்ள சாலை முழுவதும் சேதமடைந்துள்ளது. வாகனங்க |
| C16 | dept | electricity / street_lights | police | இரவு நேரத்தில் தெருவிளக்குகள் எரிவதில்லை. பெண்களும் குழந்தைக |
| C16 | severity | high | medium | இரவு நேரத்தில் தெருவிளக்குகள் எரிவதில்லை. பெண்களும் குழந்தைக |
| C17 | severity | high | medium | குடியிருப்பு பகுதியில் கழிவுநீர் கால்வாய் அடைத்துவிட்டது. து |
| C19 | severity | low | medium | பேருந்து நிறுத்தத்தில் வயதானவர்கள் உட்காருவதற்கு இருக்கைகள்  |
| C19 | urgency | routine | soon | பேருந்து நிறுத்தத்தில் வயதானவர்கள் உட்காருவதற்கு இருக்கைகள்  |
| C20 | urgency | immediate | soon | எங்கள் பகுதியில் தெருநாய்கள் கூட்டமாக சுற்றித் திரிகின்றன. ந |
| C21 | severity | high | medium | அருகிலுள்ள அரசு பள்ளியில் கழிப்பறைகள் மிகவும் மோசமான நிலையில |
| C22 | dept | public_health / public_health | electricity | மருத்துவமனையில் அவசர சிகிச்சைக்கு சென்றபோது ஆம்புலன்ஸ் வருவத |
| C22 | severity | high | medium | மருத்துவமனையில் அவசர சிகிச்சைக்கு சென்றபோது ஆம்புலன்ஸ் வருவத |
| C22 | urgency | immediate | routine | மருத்துவமனையில் அவசர சிகிச்சைக்கு சென்றபோது ஆம்புலன்ஸ் வருவத |
| C23 | severity | medium | high | எங்கள் வீட்டிற்கு வரும் மின்சாரம் அடிக்கடி போய்விடுகிறது. யா |
| C23 | urgency | soon | immediate | எங்கள் வீட்டிற்கு வரும் மின்சாரம் அடிக்கடி போய்விடுகிறது. யா |
| C24 | dept | Unclassified | transport | இங்கே ஏதோ சரியாக இல்லை. பல நாட்களாக மக்கள் சிரமப்படுகிறார்கள |
| C24 | severity | low | medium | இங்கே ஏதோ சரியாக இல்லை. பல நாட்களாக மக்கள் சிரமப்படுகிறார்கள |
| C24 | urgency | routine | soon | இங்கே ஏதோ சரியாக இல்லை. பல நாட்களாக மக்கள் சிரமப்படுகிறார்கள |
| C25 | severity | high | medium | Enga area la rendu naala water varala. Tanker kooda innum an |
| C26 | severity | medium | high | Road full ah damage aayirukku. Daily bike la pogumbodhu keez |
| C28 | severity | low | high | EB bill romba adhigama vandhurukku. Nanga use pannadha curre |
| C28 | urgency | routine | immediate | EB bill romba adhigama vandhurukku. Nanga use pannadha curre |
| C30 | severity | high | medium | Drainage water veetukulla vandhuduchu. Chinna pasanga irukka |
| C30 | urgency | immediate | soon | Drainage water veetukulla vandhuduchu. Chinna pasanga irukka |
| C31 | dept | police / Noise Pollution Control | street_lights | Enga street la yaaro night full ah loud music podraanga. Tho |
| C31 | severity | low | medium | Enga street la yaaro night full ah loud music podraanga. Tho |
| C31 | urgency | routine | soon | Enga street la yaaro night full ah loud music podraanga. Tho |
| C32 | severity | low | high | Government office la certificate apply panni romba naal aach |
| C32 | urgency | routine | soon | Government office la certificate apply panni romba naal aach |
| C34 | dept | Unclassified | electricity | Inga edho issue irukku. Nethu lendhu same problem, yaar kita |
| C34 | severity | low | high | Inga edho issue irukku. Nethu lendhu same problem, yaar kita |
| C34 | urgency | routine | soon | Inga edho issue irukku. Nethu lendhu same problem, yaar kita |
| C35 | dept | solid_waste / solid_waste | water_supply | Public toilet romba dirty ah irukku. Water um illa, cleaning |
| C35 | severity | medium | high | Public toilet romba dirty ah irukku. Water um illa, cleaning |
| C38 | severity | medium | high | Mohalle mein kachra roz jama hota ja raha hai. Safai karamch |
| C40 | dept | public_health | electricity | Sarkari hospital mein dawa available nahi hai. Patients ko b |
| C45 | dept | Unclassified | police | Pata nahi kya problem hai, lekin hamare yahan sab kuch pehle |
| C45 | severity | low | medium | Pata nahi kya problem hai, lekin hamare yahan sab kuch pehle |
| C45 | urgency | routine | soon | Pata nahi kya problem hai, lekin hamare yahan sab kuch pehle |
