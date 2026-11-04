### Baseline (TF-IDF + LogReg) on independent test, n=45

| target | acc (all rows) | acc (gold label exists in training labels) | macro-F1 |
|---|---|---|---|
| dept | 55.6% (25/45) | 75.8% (25/33) | 0.319 |
| severity | 42.2% (19/45) | 42.2% (19/45) | 0.468 |
| urgency | 62.2% (28/45) | 62.2% (28/45) | 0.542 |

| lang | n | dept correct | dept acc |
|---|---|---|---|
| en | 12 | 8 | 67% |
| hi_rom | 10 | 6 | 60% |
| ta | 12 | 4 | 33% |
| ta_rom | 11 | 7 | 64% |

#### Misses

| id | target | gold | predicted | text |
|---|---|---|---|---|
| C02 | severity | medium | high | The garbage collection vehicle has not visited our area for  |
| C05 | severity | medium | low | Someone is dumping construction waste on the empty plot besi |
| C06 | severity | high | critical | There is a strong sewage smell coming from the drainage line |
| C07 | dept | public_health | sewerage_drainage | A government hospital has been turning away patients because |
| C07 | severity | high | medium | A government hospital has been turning away patients because |
| C08 | dept | Food and Civil Supplies | encroachment | My ration card details are incorrect, and the shopkeeper ref |
| C08 | urgency | soon | routine | My ration card details are incorrect, and the shopkeeper ref |
| C10 | severity | medium | low | Buses on our route are frequently cancelled without any prio |
| C10 | urgency | soon | routine | Buses on our route are frequently cancelled without any prio |
| C11 | dept | Revenue Department | electricity | I have been trying to get my property tax receipt corrected, |
| C11 | severity | low | medium | I have been trying to get my property tax receipt corrected, |
| C11 | urgency | routine | soon | I have been trying to get my property tax receipt corrected, |
| C12 | dept | Parks and Municipal Administration | electricity | There is something wrong with the public park near our stree |
| C12 | severity | low | medium | There is something wrong with the public park near our stree |
| C12 | urgency | routine | immediate | There is something wrong with the public park near our stree |
| C14 | dept | solid_waste | public_health | தெருவில் குப்பைகள் அள்ளப்படாமல் குவிந்து கிடக்கின்றன. இதனால் |
| C15 | dept | roads | encroachment | எங்கள் தெருவில் உள்ள சாலை முழுவதும் சேதமடைந்துள்ளது. வாகனங்க |
| C16 | dept | electricity / street_lights | transport | இரவு நேரத்தில் தெருவிளக்குகள் எரிவதில்லை. பெண்களும் குழந்தைக |
| C16 | severity | high | medium | இரவு நேரத்தில் தெருவிளக்குகள் எரிவதில்லை. பெண்களும் குழந்தைக |
| C17 | severity | high | medium | குடியிருப்பு பகுதியில் கழிவுநீர் கால்வாய் அடைத்துவிட்டது. து |
| C18 | dept | Food and Civil Supplies | electricity | ரேஷன் கடையில் இந்த மாதம் அரிசி தர மறுக்கிறார்கள். என்னுடைய அ |
| C18 | severity | medium | high | ரேஷன் கடையில் இந்த மாதம் அரிசி தர மறுக்கிறார்கள். என்னுடைய அ |
| C18 | urgency | soon | immediate | ரேஷன் கடையில் இந்த மாதம் அரிசி தர மறுக்கிறார்கள். என்னுடைய அ |
| C19 | severity | low | medium | பேருந்து நிறுத்தத்தில் வயதானவர்கள் உட்காருவதற்கு இருக்கைகள்  |
| C19 | urgency | routine | immediate | பேருந்து நிறுத்தத்தில் வயதானவர்கள் உட்காருவதற்கு இருக்கைகள்  |
| C20 | dept | Animal Welfare / other | public_health | எங்கள் பகுதியில் தெருநாய்கள் கூட்டமாக சுற்றித் திரிகின்றன. ந |
| C20 | urgency | immediate | soon | எங்கள் பகுதியில் தெருநாய்கள் கூட்டமாக சுற்றித் திரிகின்றன. ந |
| C21 | dept | Education Department | roads | அருகிலுள்ள அரசு பள்ளியில் கழிப்பறைகள் மிகவும் மோசமான நிலையில |
| C21 | severity | high | medium | அருகிலுள்ள அரசு பள்ளியில் கழிப்பறைகள் மிகவும் மோசமான நிலையில |
| C22 | dept | public_health / public_health | electricity | மருத்துவமனையில் அவசர சிகிச்சைக்கு சென்றபோது ஆம்புலன்ஸ் வருவத |
| C22 | severity | high | medium | மருத்துவமனையில் அவசர சிகிச்சைக்கு சென்றபோது ஆம்புலன்ஸ் வருவத |
| C22 | urgency | immediate | routine | மருத்துவமனையில் அவசர சிகிச்சைக்கு சென்றபோது ஆம்புலன்ஸ் வருவத |
| C23 | severity | medium | high | எங்கள் வீட்டிற்கு வரும் மின்சாரம் அடிக்கடி போய்விடுகிறது. யா |
| C23 | urgency | soon | immediate | எங்கள் வீட்டிற்கு வரும் மின்சாரம் அடிக்கடி போய்விடுகிறது. யா |
| C24 | dept | Unclassified | transport | இங்கே ஏதோ சரியாக இல்லை. பல நாட்களாக மக்கள் சிரமப்படுகிறார்கள |
| C24 | severity | low | medium | இங்கே ஏதோ சரியாக இல்லை. பல நாட்களாக மக்கள் சிரமப்படுகிறார்கள |
| C24 | urgency | routine | soon | இங்கே ஏதோ சரியாக இல்லை. பல நாட்களாக மக்கள் சிரமப்படுகிறார்கள |
| C26 | severity | medium | high | Road full ah damage aayirukku. Daily bike la pogumbodhu keez |
| C28 | severity | low | high | EB bill romba adhigama vandhurukku. Nanga use pannadha curre |
| C28 | urgency | routine | immediate | EB bill romba adhigama vandhurukku. Nanga use pannadha curre |
| C30 | severity | high | medium | Drainage water veetukulla vandhuduchu. Chinna pasanga irukka |
| C30 | urgency | immediate | soon | Drainage water veetukulla vandhuduchu. Chinna pasanga irukka |
| C31 | dept | Police / Noise Pollution Control | street_lights | Enga street la yaaro night full ah loud music podraanga. Tho |
| C31 | severity | low | medium | Enga street la yaaro night full ah loud music podraanga. Tho |
| C31 | urgency | routine | soon | Enga street la yaaro night full ah loud music podraanga. Tho |
| C32 | dept | Revenue / E-Governance | water_supply | Government office la certificate apply panni romba naal aach |
| C32 | severity | low | high | Government office la certificate apply panni romba naal aach |
| C32 | urgency | routine | soon | Government office la certificate apply panni romba naal aach |
| C34 | dept | Unclassified | electricity | Inga edho issue irukku. Nethu lendhu same problem, yaar kita |
| C34 | severity | low | high | Inga edho issue irukku. Nethu lendhu same problem, yaar kita |
| C34 | urgency | routine | soon | Inga edho issue irukku. Nethu lendhu same problem, yaar kita |
| C35 | dept | solid_waste / solid_waste | water_supply | Public toilet romba dirty ah irukku. Water um illa, cleaning |
| C35 | severity | medium | high | Public toilet romba dirty ah irukku. Water um illa, cleaning |
| C35 | urgency | soon | immediate | Public toilet romba dirty ah irukku. Water um illa, cleaning |
| C38 | severity | medium | high | Mohalle mein kachra roz jama hota ja raha hai. Safai karamch |
| C40 | dept | public_health | water_supply | Sarkari hospital mein dawa available nahi hai. Patients ko b |
| C40 | severity | high | medium | Sarkari hospital mein dawa available nahi hai. Patients ko b |
| C43 | dept | Police Department | water_supply | Police station mein complaint dene gaye the, lekin abhi tak  |
| C44 | dept | Revenue Department | encroachment | Mere land document mein naam galat hai. Correction ke liye k |
| C44 | severity | medium | low | Mere land document mein naam galat hai. Correction ke liye k |
| C45 | dept | Unclassified | sewerage_drainage | Pata nahi kya problem hai, lekin hamare yahan sab kuch pehle |
| C45 | severity | low | medium | Pata nahi kya problem hai, lekin hamare yahan sab kuch pehle |
| C45 | urgency | routine | soon | Pata nahi kya problem hai, lekin hamare yahan sab kuch pehle |
