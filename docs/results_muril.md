# MuRIL multi-task fine-tune

### synthetic val (sanity only)

| target | acc (all rows) | acc (gold label exists in training labels) | macro-F1 |
|---|---|---|---|
| dept | 92.9% (585/630) | 92.9% (585/630) | 0.926 |
| severity | 100.0% (630/630) | 100.0% (630/630) | 1.000 |
| urgency | 99.7% (628/630) | 99.7% (628/630) | 0.997 |

| lang | n | dept correct | dept acc |
|---|---|---|---|
| en | 128 | 122 | 95% |
| hi_rom | 83 | 76 | 92% |
| mixed | 166 | 159 | 96% |
| ta | 91 | 81 | 89% |
| ta_rom | 162 | 147 | 91% |

### seed test (20)

| target | acc (all rows) | acc (gold label exists in training labels) | macro-F1 |
|---|---|---|---|
| dept | 85.0% (17/20) | 85.0% (17/20) | 0.802 |
| severity | 75.0% (15/20) | 75.0% (15/20) | 0.685 |
| urgency | 90.0% (18/20) | 90.0% (18/20) | 0.871 |

| lang | n | dept correct | dept acc |
|---|---|---|---|
| en | 6 | 5 | 83% |
| hi_rom | 4 | 3 | 75% |
| ta | 4 | 4 | 100% |
| ta_rom | 6 | 5 | 83% |

### independent test (45)

| target | acc (all rows) | acc (gold label exists in training labels) | macro-F1 |
|---|---|---|---|
| dept | 48.9% (22/45) | 66.7% (22/33) | 0.266 |
| severity | 44.4% (20/45) | 44.4% (20/45) | 0.406 |
| urgency | 60.0% (27/45) | 60.0% (27/45) | 0.491 |

| lang | n | dept correct | dept acc |
|---|---|---|---|
| en | 12 | 6 | 50% |
| hi_rom | 10 | 5 | 50% |
| ta | 12 | 6 | 50% |
| ta_rom | 11 | 5 | 45% |

#### Misses (independent)

| id | target | gold | predicted | text |
|---|---|---|---|---|
| C01 | severity | high | medium | There has been no water supply in our street since yesterday |
| C03 | dept | roads | sewerage_drainage | A large pothole has developed near the main junction. Two-wh |
| C05 | dept | other | solid_waste | Someone is dumping construction waste on the empty plot besi |
| C05 | urgency | routine | soon | Someone is dumping construction waste on the empty plot besi |
| C06 | severity | high | critical | There is a strong sewage smell coming from the drainage line |
| C07 | dept | public_health | sewerage_drainage | A government hospital has been turning away patients because |
| C07 | severity | high | medium | A government hospital has been turning away patients because |
| C08 | dept | Food and Civil Supplies | sewerage_drainage | My ration card details are incorrect, and the shopkeeper ref |
| C10 | severity | medium | low | Buses on our route are frequently cancelled without any prio |
| C10 | urgency | soon | routine | Buses on our route are frequently cancelled without any prio |
| C11 | dept | Revenue Department | sewerage_drainage | I have been trying to get my property tax receipt corrected, |
| C11 | severity | low | medium | I have been trying to get my property tax receipt corrected, |
| C11 | urgency | routine | soon | I have been trying to get my property tax receipt corrected, |
| C12 | dept | Parks and Municipal Administration | roads | There is something wrong with the public park near our stree |
| C12 | severity | low | medium | There is something wrong with the public park near our stree |
| C12 | urgency | routine | soon | There is something wrong with the public park near our stree |
| C13 | severity | high | medium | எங்கள் பகுதியில் கடந்த மூன்று நாட்களாக குடிநீர் வரவில்லை. அத |
| C16 | severity | high | medium | இரவு நேரத்தில் தெருவிளக்குகள் எரிவதில்லை. பெண்களும் குழந்தைக |
| C17 | severity | high | medium | குடியிருப்பு பகுதியில் கழிவுநீர் கால்வாய் அடைத்துவிட்டது. து |
| C18 | dept | Food and Civil Supplies | sewerage_drainage | ரேஷன் கடையில் இந்த மாதம் அரிசி தர மறுக்கிறார்கள். என்னுடைய அ |
| C19 | dept | transport | sewerage_drainage | பேருந்து நிறுத்தத்தில் வயதானவர்கள் உட்காருவதற்கு இருக்கைகள்  |
| C19 | severity | low | medium | பேருந்து நிறுத்தத்தில் வயதானவர்கள் உட்காருவதற்கு இருக்கைகள்  |
| C19 | urgency | routine | soon | பேருந்து நிறுத்தத்தில் வயதானவர்கள் உட்காருவதற்கு இருக்கைகள்  |
| C20 | dept | Animal Welfare / other | public_health | எங்கள் பகுதியில் தெருநாய்கள் கூட்டமாக சுற்றித் திரிகின்றன. ந |
| C20 | urgency | immediate | soon | எங்கள் பகுதியில் தெருநாய்கள் கூட்டமாக சுற்றித் திரிகின்றன. ந |
| C21 | dept | Education Department | roads | அருகிலுள்ள அரசு பள்ளியில் கழிப்பறைகள் மிகவும் மோசமான நிலையில |
| C21 | severity | high | medium | அருகிலுள்ள அரசு பள்ளியில் கழிப்பறைகள் மிகவும் மோசமான நிலையில |
| C22 | dept | public_health / public_health | transport | மருத்துவமனையில் அவசர சிகிச்சைக்கு சென்றபோது ஆம்புலன்ஸ் வருவத |
| C22 | severity | high | low | மருத்துவமனையில் அவசர சிகிச்சைக்கு சென்றபோது ஆம்புலன்ஸ் வருவத |
| C22 | urgency | immediate | routine | மருத்துவமனையில் அவசர சிகிச்சைக்கு சென்றபோது ஆம்புலன்ஸ் வருவத |
| C23 | urgency | soon | routine | எங்கள் வீட்டிற்கு வரும் மின்சாரம் அடிக்கடி போய்விடுகிறது. யா |
| C24 | dept | Unclassified | sewerage_drainage | இங்கே ஏதோ சரியாக இல்லை. பல நாட்களாக மக்கள் சிரமப்படுகிறார்கள |
| C24 | severity | low | medium | இங்கே ஏதோ சரியாக இல்லை. பல நாட்களாக மக்கள் சிரமப்படுகிறார்கள |
| C24 | urgency | routine | soon | இங்கே ஏதோ சரியாக இல்லை. பல நாட்களாக மக்கள் சிரமப்படுகிறார்கள |
| C25 | severity | high | medium | Enga area la rendu naala water varala. Tanker kooda innum an |
| C26 | severity | medium | high | Road full ah damage aayirukku. Daily bike la pogumbodhu keez |
| C27 | dept | solid_waste | sewerage_drainage | Corporation garbage collect panna varave illa. Street la rom |
| C27 | severity | medium | critical | Corporation garbage collect panna varave illa. Street la rom |
| C27 | urgency | soon | immediate | Corporation garbage collect panna varave illa. Street la rom |
| C28 | severity | low | high | EB bill romba adhigama vandhurukku. Nanga use pannadha curre |
| C28 | urgency | routine | immediate | EB bill romba adhigama vandhurukku. Nanga use pannadha curre |
| C29 | dept | transport | street_lights | Bus driver stop la niruthama poitaaru. Daily idhe problem dh |
| C30 | severity | high | medium | Drainage water veetukulla vandhuduchu. Chinna pasanga irukka |
| C30 | urgency | immediate | soon | Drainage water veetukulla vandhuduchu. Chinna pasanga irukka |
| C31 | dept | Police / Noise Pollution Control | other | Enga street la yaaro night full ah loud music podraanga. Tho |
| C32 | dept | Revenue / E-Governance | sewerage_drainage | Government office la certificate apply panni romba naal aach |
| C32 | severity | low | high | Government office la certificate apply panni romba naal aach |
| C32 | urgency | routine | immediate | Government office la certificate apply panni romba naal aach |
| C33 | severity | critical | high | Oru transformer la irundhu smoke varudhu. Pakkathula neraya  |
| C34 | dept | Unclassified | sewerage_drainage | Inga edho issue irukku. Nethu lendhu same problem, yaar kita |
| C34 | severity | low | medium | Inga edho issue irukku. Nethu lendhu same problem, yaar kita |
| C34 | urgency | routine | soon | Inga edho issue irukku. Nethu lendhu same problem, yaar kita |
| C35 | dept | solid_waste / solid_waste | sewerage_drainage | Public toilet romba dirty ah irukku. Water um illa, cleaning |
| C37 | dept | roads | sewerage_drainage | Sadak par bahut bade gaddhe hain. Kal ek bike wala gir gaya  |
| C37 | urgency | soon | immediate | Sadak par bahut bade gaddhe hain. Kal ek bike wala gir gaya  |
| C39 | severity | low | high | Bijli ka bill achanak double aa gaya hai. Meter reading bhi  |
| C39 | urgency | routine | immediate | Bijli ka bill achanak double aa gaya hai. Meter reading bhi  |
| C40 | dept | public_health | water_supply | Sarkari hospital mein dawa available nahi hai. Patients ko b |
| C40 | severity | high | medium | Sarkari hospital mein dawa available nahi hai. Patients ko b |
| C43 | dept | Police Department | public_health | Police station mein complaint dene gaye the, lekin abhi tak  |
| C43 | severity | medium | high | Police station mein complaint dene gaye the, lekin abhi tak  |
| C44 | dept | Revenue Department | sewerage_drainage | Mere land document mein naam galat hai. Correction ke liye k |
| C44 | urgency | routine | soon | Mere land document mein naam galat hai. Correction ke liye k |
| C45 | dept | Unclassified | sewerage_drainage | Pata nahi kya problem hai, lekin hamare yahan sab kuch pehle |
| C45 | severity | low | medium | Pata nahi kya problem hai, lekin hamare yahan sab kuch pehle |
| C45 | urgency | routine | soon | Pata nahi kya problem hai, lekin hamare yahan sab kuch pehle |
