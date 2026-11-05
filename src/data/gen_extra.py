"""Generate extra training rows for departments missing from synth.jsonl, then write synth_v2.jsonl.
    python src/data/gen_extra.py
"""
import json, random, collections
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

random.seed(7)
N_PER_DEPT = 300
SRC, EXTRA, OUT = "data/processed/synth.jsonl", "data/processed/synth_extra.jsonl", "data/processed/synth_v2.jsonl"

AREAS = ["Adambakkam", "Velachery", "Perambur", "T Nagar", "Anna Nagar", "Tambaram", "Mylapore", "Guindy", "Kodambakkam",
         "Royapuram", "Saidapet", "Porur", "Ambattur", "Chromepet", "Tondiarpet", "Besant Nagar", "Washermanpet", "Madipakkam"]

PRE = {"en": ["", "", "", "Sir, ", "Madam, ", "Request: ", "Complaint: ", "Urgent: ", "Kindly note, "],
       "ta": ["", "", "", "ஐயா, ", "அம்மா, ", "வணக்கம், "],
       "ta_rom": ["", "", "", "Sir ", "Anna ", "Amma ", "Vanakkam, "],
       "hi_rom": ["", "", "", "Sir ", "Madam ", "Namaste, ", "Bhaiya "]}
SUF = {"en": ["", "", ".", ". Kindly resolve soon.", ". Please take action.", ". This has been going on for long.", ". Waiting for a response."],
       "ta": ["", "", "", " தயவுசெய்து நடவடிக்கை எடுங்கள்", " விரைவில் தீர்வு வேண்டும்"],
       "ta_rom": ["", "", "", " please action edunga", " seekiram paarunga", " romba naala aachu"],
       "hi_rom": ["", "", "", " jaldi dekhiye", " kripya karwai karein", " kaafi din ho gaye"]}
LOC = {"en": ["", "", "in {a}, ", "near {a}, ", "around {a}: "],
       "ta": ["", "", "{a} பகுதியில் ", "{a} அருகில் "],
       "ta_rom": ["", "", "{a} la ", "{a} pakkathula "],
       "hi_rom": ["", "", "{a} mein ", "{a} ke paas "]}

PHRASES = {
 "revenue": {
  "en": [("my patta transfer has been pending for months and the office keeps asking for more documents", "medium", "routine"),
         ("the income certificate application was rejected without any reason being given", "low", "routine"),
         ("there is a mistake in the survey number on my land record and nobody is correcting it", "medium", "routine"),
         ("the village officer is demanding a bribe to issue the legal heir certificate", "high", "soon"),
         ("we have been waiting for weeks to register a sale document at the sub-registrar office", "medium", "soon"),
         ("the encumbrance certificate cannot be obtained and the officers keep sending us away", "low", "routine")],
  "ta": [("பட்டா மாற்றம் செய்ய பல மாதங்களாக காத்திருக்கிறேன், அலுவலகத்தில் யாரும் பதில் சொல்வதில்லை", "medium", "routine"),
         ("வருமான சான்றிதழ் விண்ணப்பம் எந்த காரணமும் சொல்லாமல் நிராகரிக்கப்பட்டது", "low", "routine"),
         ("நிலப் பதிவேட்டில் சர்வே எண் தவறாக உள்ளது, யாரும் திருத்தவில்லை", "medium", "routine"),
         ("வாரிசு சான்றிதழ் வழங்க கிராம நிர்வாக அலுவலர் லஞ்சம் கேட்கிறார்", "high", "soon"),
         ("பத்திரப்பதிவு அலுவலகத்தில் ஆவணம் பதிவு செய்ய வாரக்கணக்கில் காத்திருக்க வேண்டியுள்ளது", "medium", "soon")],
  "ta_rom": [("patta mattram panna romba maadhama alaiyarom, office la yaarum badhil solla maatraanga", "medium", "routine"),
             ("income certificate ye reject pannaanga nu kaaranam kooda sollala", "low", "routine"),
             ("land record la survey number thappa irukku, yaarum sari panna maatraanga", "medium", "routine"),
             ("legal heir certificate kudukka VAO panam kekkuraaru", "high", "soon"),
             ("registrar office la document register panna vaaram kanakka kaathirukka vendiyirukku", "medium", "soon")],
  "hi_rom": [("patta transfer ke liye kai mahine se chakkar kaat raha hoon, koi sunta nahi", "medium", "routine"),
             ("income certificate ka application bina wajah bataye reject kar diya gaya", "low", "routine"),
             ("zameen ke record mein survey number galat likha hai, koi theek nahi kar raha", "medium", "routine"),
             ("legal heir certificate dene ke liye patwari paise maang raha hai", "high", "soon"),
             ("registry office mein document register karne ke liye hafton intezaar karna pad raha hai", "medium", "soon")]},
 "police": {
  "en": [("a group of men drink and create trouble near the bus stop every night", "medium", "soon"),
         ("my bike was stolen last week and the police are not registering an FIR", "high", "soon"),
         ("chain snatching has increased on our street and there is no night patrolling", "high", "soon"),
         ("banned tobacco and liquor are being sold illegally near the school", "high", "soon"),
         ("vehicles keep jumping the signal because no traffic police are posted at the junction", "medium", "routine"),
         ("a stranger has been threatening our family and we are afraid to step out", "high", "immediate")],
  "ta": [("இரவு நேரத்தில் பேருந்து நிறுத்தம் அருகே சிலர் குடித்துவிட்டு தொந்தரவு செய்கிறார்கள்", "medium", "soon"),
         ("என் வாகனம் திருடப்பட்டது, போலீசார் புகாரை பதிவு செய்ய மறுக்கிறார்கள்", "high", "soon"),
         ("எங்கள் தெருவில் செயின் பறிப்பு அதிகரித்துள்ளது, இரவில் ரோந்து இல்லை", "high", "soon"),
         ("பள்ளி அருகே சட்டவிரோதமாக புகையிலை பொருட்கள் விற்கப்படுகின்றன", "high", "soon"),
         ("சந்திப்பில் போக்குவரத்து போலீசார் இல்லாததால் வாகனங்கள் சிக்னலை மீறுகின்றன", "medium", "routine"),
         ("ஒரு நபர் எங்கள் குடும்பத்தை மிரட்டுகிறார், வெளியே செல்லவே பயமாக உள்ளது", "high", "immediate")],
  "ta_rom": [("night time la bus stop pakkathula konjam peru kudichittu thollai panraanga", "medium", "soon"),
             ("en bike thirudu poiduchu, police FIR podave maatraanga", "high", "soon"),
             ("enga street la chain snatching adhigam aayiduchu, raathri patrol ve illa", "high", "soon"),
             ("school pakkathula gutka, sarakku ellam illegal ah vikkiraanga", "high", "soon"),
             ("oruthar enga kudumbatha miratturaaru, veliya pogave bayama irukku", "high", "immediate")],
  "hi_rom": [("raat ko bus stop ke paas kuch log sharaab peekar hungama karte hain", "medium", "soon"),
             ("meri bike chori ho gayi hai aur police FIR likhne se mana kar rahi hai", "high", "soon"),
             ("hamari gali mein chain snatching badh gayi hai, raat ko patrolling nahi hoti", "high", "soon"),
             ("school ke paas gutka aur sharaab chhupke se bechi ja rahi hai", "high", "soon"),
             ("ek aadmi hamare parivar ko dhamka raha hai, bahar nikalne mein darr lagta hai", "high", "immediate")]},
 "education": {
  "en": [("the government school has no mathematics teacher and the exams are very near", "high", "soon"),
         ("classrooms in the school leak whenever it rains and the children cannot sit", "high", "soon"),
         ("the midday meal served at the school is of poor quality", "high", "soon"),
         ("benches and desks in the school are broken and students sit on the floor", "medium", "routine"),
         ("the school management is demanding a donation before giving admission", "medium", "soon"),
         ("the school has no science laboratory equipment even though the practical exams are close", "medium", "routine")],
  "ta": [("அரசு பள்ளியில் கணித ஆசிரியர் இல்லை, தேர்வு நெருங்கிவிட்டது", "high", "soon"),
         ("மழை பெய்தால் பள்ளி வகுப்பறைகளில் தண்ணீர் ஒழுகுகிறது, குழந்தைகள் உட்கார முடியவில்லை", "high", "soon"),
         ("பள்ளியில் வழங்கப்படும் மதிய உணவு தரமற்றதாக உள்ளது", "high", "soon"),
         ("பள்ளியில் மேசை, நாற்காலிகள் உடைந்து கிடக்கின்றன, மாணவர்கள் தரையில் உட்கார்கிறார்கள்", "medium", "routine"),
         ("சேர்க்கைக்கு முன் பள்ளி நிர்வாகம் நன்கொடை கேட்கிறது", "medium", "soon")],
  "ta_rom": [("govt school la maths teacher illa, exam kitta vandhuduchu", "high", "soon"),
             ("mazhai peinjaa school classroom la thanni ozhugudhu, pasanga okkara mudiyala", "high", "soon"),
             ("school la kudukkura mid-day meal romba mosama irukku", "high", "soon"),
             ("school la bench, desk ellam odanju kidakku, pasanga tharazhaiyila okkaraanga", "medium", "routine"),
             ("admission ku munnaadi school la donation kekkuraanga", "medium", "soon")],
  "hi_rom": [("sarkari school mein maths ke teacher nahi hain aur exam paas aa gaye hain", "high", "soon"),
             ("barish mein school ki classroom ki chhat tapakti hai, bachche baith nahi paate", "high", "soon"),
             ("school mein milne wala mid-day meal bahut kharab quality ka hai", "high", "soon"),
             ("school mein bench aur desk toote hue hain, bachche zameen par baithte hain", "medium", "routine"),
             ("admission se pehle school donation maang raha hai", "medium", "soon")]},
 "food_civil_supplies": {
  "en": [("the ration shop remains closed on most days and cardholders cannot collect their quota", "medium", "soon"),
         ("the fair price shop gives less sugar and wheat than the allotted quantity", "medium", "routine"),
         ("my name has been removed from the family card after the recent update", "medium", "soon"),
         ("the ration shop owner asks for extra money for every item", "medium", "soon"),
         ("the smart card application is pending and I cannot get any subsidy", "medium", "routine"),
         ("the rice given at the ration shop is full of stones and smells bad", "medium", "soon")],
  "ta": [("ரேஷன் கடை பெரும்பாலான நாட்கள் மூடியே இருக்கிறது, பொருட்கள் வாங்க முடியவில்லை", "medium", "soon"),
         ("நியாய விலைக் கடையில் சர்க்கரை, கோதுமை அளவில் குறைத்து தருகிறார்கள்", "medium", "routine"),
         ("குடும்ப அட்டையில் இருந்து என் பெயர் நீக்கப்பட்டுள்ளது", "medium", "soon"),
         ("ரேஷன் கடையில் ஒவ்வொரு பொருளுக்கும் கூடுதல் பணம் கேட்கிறார்கள்", "medium", "soon"),
         ("ரேஷனில் கொடுக்கும் அரிசியில் கற்கள் அதிகமாக உள்ளன, வாசனையும் சரியில்லை", "medium", "soon")],
  "ta_rom": [("ration kadai romba naal moodiye irukku, porul vaanga mudiyala", "medium", "soon"),
             ("ration kadai la sugar, wheat alavu korachi tharaanga", "medium", "routine"),
             ("family card la irundhu en peru neekkitaanga, ippo ethuvum kidaikkala", "medium", "soon"),
             ("ration kadai la ovvoru porulukkum extra panam kekkuraanga", "medium", "soon"),
             ("ration arisi la kal romba irukku, vaasanaiyum sari illa", "medium", "soon")],
  "hi_rom": [("ration dukaan zyadatar din band rehti hai, card holders ko saaman nahi milta", "medium", "soon"),
             ("ration dukaan par cheeni aur gehun tay matra se kam diya ja raha hai", "medium", "routine"),
             ("family card se mera naam hata diya gaya hai, ab koi saaman nahi mil raha", "medium", "soon"),
             ("ration dukaandaar har cheez ke liye extra paise maang raha hai", "medium", "soon"),
             ("ration ka chawal ganda hai, usme kankad bahut hain", "medium", "soon")]},
 "parks": {
  "en": [("the play equipment for children in the park is broken and rusted", "medium", "routine"),
         ("the park lights are not working so nobody can walk there in the evening", "medium", "soon"),
         ("the grass in the park has not been cut for months and snakes have been seen", "high", "soon"),
         ("the walking track in the park is damaged and people are tripping", "medium", "routine"),
         ("the park gate stays locked in the early morning when senior citizens want to walk", "low", "routine"),
         ("people are throwing garbage and drinking alcohol inside the park", "medium", "soon")],
  "ta": [("பூங்காவில் குழந்தைகள் விளையாடும் கருவிகள் உடைந்து துருப்பிடித்துள்ளன", "medium", "routine"),
         ("பூங்காவில் விளக்குகள் எரியாததால் மாலையில் நடக்க முடியவில்லை", "medium", "soon"),
         ("பூங்காவில் புல் பல மாதங்களாக வெட்டப்படவில்லை, பாம்புகள் தென்படுகின்றன", "high", "soon"),
         ("பூங்கா நடைபாதை சேதமடைந்து மக்கள் தடுக்கி விழுகிறார்கள்", "medium", "routine"),
         ("பூங்காவுக்குள் சிலர் குப்பை போட்டு மது அருந்துகிறார்கள்", "medium", "soon")],
  "ta_rom": [("park la pasanga vilaiyaadura equipment odanju thuru pidichi irukku", "medium", "routine"),
             ("park la light eriyaadhadhaala saayangaalam nadakka mudiyala", "medium", "soon"),
             ("park la pul maasa kanakka vetta ala, paambu ellam theriyudhu", "high", "soon"),
             ("park walking track udanju makkal thadukki vizhuraanga", "medium", "routine"),
             ("park ulla yaaro kuppai potturaanga, kudikkavum seiraanga", "medium", "soon")],
  "hi_rom": [("park mein bachchon ke jhoole aur khel ke saaman toote aur zang lage hain", "medium", "routine"),
             ("park ki lights band hain isliye shaam ko koi tehal nahi sakta", "medium", "soon"),
             ("park mein ghaas mahino se nahi kati, saanp dikh rahe hain", "high", "soon"),
             ("park ka walking track tuta hua hai, log gir rahe hain", "medium", "routine"),
             ("park ke andar log kachra phenk rahe hain aur sharaab pi rahe hain", "medium", "soon")]},
 "animal_control": {
  "en": [("stray dogs chase two-wheelers and children on our street every evening", "high", "soon"),
         ("a pack of dogs is aggressive near the school gate and parents are scared", "high", "soon"),
         ("a dead animal has been lying on the road for two days and nobody has removed it", "medium", "soon"),
         ("cattle roam on the main road and cause accidents", "high", "soon"),
         ("a snake has been found inside our apartment compound and needs to be removed", "high", "immediate"),
         ("street dogs in our locality have not been vaccinated or sterilised for years", "medium", "routine")],
  "ta": [("தெருநாய்கள் தினமும் மாலையில் இருசக்கர வாகனங்களை துரத்துகின்றன", "high", "soon"),
         ("பள்ளி வாசல் அருகே நாய்கள் கூட்டம் ஆக்ரோஷமாக உள்ளது, பெற்றோர்கள் பயப்படுகிறார்கள்", "high", "soon"),
         ("இறந்த விலங்கு இரண்டு நாட்களாக சாலையில் கிடக்கிறது, யாரும் அகற்றவில்லை", "medium", "soon"),
         ("மாடுகள் பிரதான சாலையில் திரிவதால் விபத்துகள் நடக்கின்றன", "high", "soon"),
         ("எங்கள் பகுதியில் தெருநாய்களுக்கு தடுப்பூசி, கருத்தடை எதுவும் செய்யவில்லை", "medium", "routine")],
  "ta_rom": [("street naai ellam daily saayangaalam bike ah thurathudhu", "high", "soon"),
             ("school gate pakkathula naai koottam romba aggressive ah irukku, parents bayappaduraanga", "high", "soon"),
             ("setthu pona maadu rendu naala road la kedakku, yaarum edukkala", "medium", "soon"),
             ("maadu ellam main road la suthuradhaala accident aagudhu", "high", "soon"),
             ("enga area la naai ku vaccine, sterilisation edhuvum panna maattengiraanga", "medium", "routine")],
  "hi_rom": [("awara kutte roz shaam ko bike aur bachchon ke peeche padte hain", "high", "soon"),
             ("school gate ke paas kutton ka jhund bahut khatarnak hai, maa-baap darte hain", "high", "soon"),
             ("mara hua janwar do din se sadak par pada hai, koi utha nahi raha", "medium", "soon"),
             ("gaaye aur saand main road par ghoomte hain aur accident hote hain", "high", "soon"),
             ("hamare ilake mein kutton ka tikakaran aur nasbandi kabhi nahi hui", "medium", "routine")]},
}

LANGS, WEIGHTS = ["en", "ta", "ta_rom", "hi_rom"], [0.30, 0.20, 0.25, 0.25]

def compose(lang, core):
    loc = random.choice(LOC[lang]).format(a=random.choice(AREAS))
    t = random.choice(PRE[lang]) + loc + core + random.choice(SUF[lang])
    return t[0].upper() + t[1:]

existing = collections.Counter(json.loads(l)["dept"] for l in open(SRC, encoding="utf-8-sig") if l.strip())
print("already in synth.jsonl:", sorted(set(PHRASES) & set(existing)) or "none of the new departments")

rows, seen = [], set()
for dept, bank in PHRASES.items():
    made = tries = 0
    while made < N_PER_DEPT and tries < N_PER_DEPT * 60:
        tries += 1
        lang = random.choices(LANGS, WEIGHTS)[0]
        core, sev, urg = random.choice(bank[lang])
        text = compose(lang, core)
        if text in seen: continue
        seen.add(text); made += 1
        rows.append({"id": f"x{len(rows):05d}", "text": text, "lang": lang, "dept": dept, "also": [], "severity": sev, "urgency": urg,
                     "locations": [], "ward_no": None, "ward_kind": "none", "ambiguous": False, "candidates": [],
                     "split": "val" if random.random() < 0.15 else "train", "source": "synthetic_v2"})

print("new rows per department:", dict(collections.Counter(r["dept"] for r in rows)))
print("new rows per language:  ", dict(collections.Counter(r["lang"] for r in rows)))
print("new rows per split:     ", dict(collections.Counter(r["split"] for r in rows)))

indep = [json.loads(l)["text"] for l in open("data/processed/indep_test.jsonl", encoding="utf-8-sig") if l.strip()]
vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True).fit([r["text"] for r in rows] + indep)
S = cosine_similarity(vec.transform(indep), vec.transform([r["text"] for r in rows]))
mx = S.max(axis=1)
print(f"leakage check: each test complaint vs closest new training row: mean {mx.mean():.2f}, max {mx.max():.2f}")
for i in mx.argsort()[::-1][:3]:
    print(f"  {mx[i]:.2f}  test: {indep[i][:55]} | train: {rows[int(S[i].argmax())]['text'][:55]}")

with open(EXTRA, "w", encoding="utf-8") as f:
    for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
old = [l for l in open(SRC, encoding="utf-8-sig") if l.strip()]
with open(OUT, "w", encoding="utf-8") as f:
    for l in old: f.write(l.rstrip("\n") + "\n")
    for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(f"wrote {len(rows)} rows -> {EXTRA}; merged total {len(old) + len(rows)} rows -> {OUT}")
