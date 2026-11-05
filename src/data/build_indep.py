"""Build indep_test.jsonl from the 45 hand-written complaints (embedded below).  python src/data/build_indep.py"""
import json, re

OUT, SYNTH = "data/processed/indep_test.jsonl", "data/processed/synth_v2.jsonl"

DATA = """
C01|There has been no water supply in our street since yesterday morning. Several families are struggling to manage their daily activities.|Water Supply|High|Soon
C02|The garbage collection vehicle has not visited our area for almost a week. Waste is piling up near the residential buildings.|Sanitation|Medium|Soon
C03|A large pothole has developed near the main junction. Two-wheelers are swerving dangerously to avoid it.|Roads and Highways|High|Soon
C04|The streetlights outside our apartment have stopped working. It becomes completely dark after sunset.|Electricity|Medium|Soon
C05|Someone is dumping construction waste on the empty plot beside our house. Nobody seems to be doing anything about it.|Municipal Corporation|Medium|Routine
C06|There is a strong sewage smell coming from the drainage line, and dirty water is entering nearby houses.|Sewerage and Drainage|High|Immediate
C07|A government hospital has been turning away patients because there are not enough doctors available.|Public Health|High|Soon
C08|My ration card details are incorrect, and the shopkeeper refuses to provide my monthly provisions.|Food and Civil Supplies|Medium|Soon
C09|An exposed electrical wire is hanging dangerously low near a crowded bus stop. Someone could get electrocuted.|Electricity|Critical|Immediate
C10|Buses on our route are frequently cancelled without any prior notice. Students and office workers are reaching late every day.|Public Transport|Medium|Soon
C11|I have been trying to get my property tax receipt corrected, but the office keeps sending me from one counter to another.|Revenue Department|Low|Routine
C12|There is something wrong with the public park near our street. It has become difficult for residents to use it.|Parks and Municipal Administration|Low|Routine
C13|எங்கள் பகுதியில் கடந்த மூன்று நாட்களாக குடிநீர் வரவில்லை. அதிகாரிகளிடம் புகார் கொடுத்தும் எந்த நடவடிக்கையும் எடுக்கவில்லை.|Water Supply|High|Soon
C14|தெருவில் குப்பைகள் அள்ளப்படாமல் குவிந்து கிடக்கின்றன. இதனால் கொசுக்கள் அதிகமாகிவிட்டன.|Sanitation|Medium|Soon
C15|எங்கள் தெருவில் உள்ள சாலை முழுவதும் சேதமடைந்துள்ளது. வாகனங்களில் செல்வது மிகவும் சிரமமாக இருக்கிறது.|Roads and Highways|Medium|Routine
C16|இரவு நேரத்தில் தெருவிளக்குகள் எரிவதில்லை. பெண்களும் குழந்தைகளும் அந்த வழியாக செல்ல பயப்படுகிறார்கள்.|Electricity|High|Soon
C17|குடியிருப்பு பகுதியில் கழிவுநீர் கால்வாய் அடைத்துவிட்டது. துர்நாற்றம் தாங்க முடியவில்லை.|Sewerage and Drainage|High|Soon
C18|ரேஷன் கடையில் இந்த மாதம் அரிசி தர மறுக்கிறார்கள். என்னுடைய அட்டையில் எந்த பிரச்சனையும் இல்லை.|Food and Civil Supplies|Medium|Soon
C19|பேருந்து நிறுத்தத்தில் வயதானவர்கள் உட்காருவதற்கு இருக்கைகள் இல்லை. நீண்ட நேரம் நின்றுகொண்டே இருக்க வேண்டியுள்ளது.|Public Transport|Low|Routine
C20|எங்கள் பகுதியில் தெருநாய்கள் கூட்டமாக சுற்றித் திரிகின்றன. நேற்று ஒரு குழந்தையை கடித்துவிட்டது.|Animal Welfare / Municipal Corporation|High|Immediate
C21|அருகிலுள்ள அரசு பள்ளியில் கழிப்பறைகள் மிகவும் மோசமான நிலையில் உள்ளன. மாணவர்கள் பயன்படுத்த முடியவில்லை.|Education Department|High|Soon
C22|மருத்துவமனையில் அவசர சிகிச்சைக்கு சென்றபோது ஆம்புலன்ஸ் வருவதற்கு மிகவும் தாமதமானது.|Public Health / Emergency Medical Services|High|Immediate
C23|எங்கள் வீட்டிற்கு வரும் மின்சாரம் அடிக்கடி போய்விடுகிறது. யாரிடம் புகார் செய்வது என்று தெரியவில்லை.|Electricity|Medium|Soon
C24|இங்கே ஏதோ சரியாக இல்லை. பல நாட்களாக மக்கள் சிரமப்படுகிறார்கள், ஆனால் யாரும் வந்து பார்க்கவில்லை.|Unclassified|Low|Routine
C25|Enga area la rendu naala water varala. Tanker kooda innum anuppala.|Water Supply|High|Soon
C26|Road full ah damage aayirukku. Daily bike la pogumbodhu keezha vizhara maari irukku.|Roads and Highways|Medium|Soon
C27|Corporation garbage collect panna varave illa. Street la romba mosama smell varudhu.|Sanitation|Medium|Soon
C28|EB bill romba adhigama vandhurukku. Nanga use pannadha current ku ivlo amount epdi?|Electricity Board|Low|Routine
C29|Bus driver stop la niruthama poitaaru. Daily idhe problem dhaan, students romba kashtapadrom.|Public Transport|Medium|Soon
C30|Drainage water veetukulla vandhuduchu. Chinna pasanga irukkaanga, romba bayama irukku.|Sewerage and Drainage|High|Immediate
C31|Enga street la yaaro night full ah loud music podraanga. Thoongave mudiyala.|Police / Noise Pollution Control|Low|Routine
C32|Government office la certificate apply panni romba naal aachu. Innum status update eh illa.|Revenue / E-Governance|Low|Routine
C33|Oru transformer la irundhu smoke varudhu. Pakkathula neraya houses irukku, seekiram check pannunga.|Electricity|Critical|Immediate
C34|Inga edho issue irukku. Nethu lendhu same problem, yaar kitayum solli use illa.|Unclassified|Low|Routine
C35|Public toilet romba dirty ah irukku. Water um illa, cleaning um pannala.|Sanitation / Public Toilets|Medium|Soon
C36|Hamare area mein teen din se paani nahi aa raha hai. Tanker bhi abhi tak nahi bheja gaya.|Water Supply|High|Soon
C37|Sadak par bahut bade gaddhe hain. Kal ek bike wala gir gaya tha aur use chot bhi lagi.|Roads and Highways|High|Soon
C38|Mohalle mein kachra roz jama hota ja raha hai. Safai karamchari kai din se nahi aaye.|Sanitation|Medium|Soon
C39|Bijli ka bill achanak double aa gaya hai. Meter reading bhi galat lag rahi hai.|Electricity Board|Low|Routine
C40|Sarkari hospital mein dawa available nahi hai. Patients ko bahar se medicines kharidni pad rahi hain.|Public Health|High|Soon
C41|Hamare ghar ke paas ek khula manhole hai. Raat mein dikhai nahi deta, koi bhi gir sakta hai.|Sewerage and Drainage|Critical|Immediate
C42|Bus service ka timing bilkul fixed nahi hai. Office pahunchne mein roz dikkat hoti hai.|Public Transport|Medium|Soon
C43|Police station mein complaint dene gaye the, lekin abhi tak koi response nahi mila.|Police Department|Medium|Soon
C44|Mere land document mein naam galat hai. Correction ke liye kai baar apply kiya, par kuch nahi hua.|Revenue Department|Medium|Routine
C45|Pata nahi kya problem hai, lekin hamare yahan sab kuch pehle se zyada kharab ho gaya hai. Koi dekhne bhi nahi aata.|Unclassified|Low|Routine
"""

EXTRA_OK = {"C04": ["street_lights"], "C16": ["street_lights"]}   # streetlight complaints you labelled Electricity
CANDS = {
    "animal_welfare": ["animal_control"],
    "roads_highways": ["roads"], "public_transport": ["transport"], "electricity_board": ["electricity"],
    "sanitation": ["sanitation", "solid_waste", "garbage", "waste_management"],
    "public_toilets": ["sanitation", "solid_waste", "public_toilets"],
    "food_civil_supplies": ["food_civil_supplies", "civil_supplies", "ration", "pds"],
    "revenue_department": ["revenue"], "revenue": ["revenue"], "e_governance": ["revenue", "e_governance"],
    "parks_municipal_administration": ["parks", "municipal_corporation"],
    "municipal_corporation": ["municipal_corporation", "general", "other"],
    "police_department": ["police"], "police": ["police"],
    "education_department": ["education", "schools"], "emergency_medical_services": ["public_health"],
}

known = {t: set() for t in ("dept", "severity", "urgency")}
for l in open(SYNTH, encoding="utf-8-sig"):
    r = json.loads(l)
    for t in known: known[t].add(r[t])

def norm(s):
    s = re.sub(r"[^a-z0-9]+", "_", s.lower())
    return "_".join(p for p in s.split("_") if p and p != "and")

def map_dept(d):
    d = d.strip()
    if d.startswith("Unclassified"): return "Unclassified"
    n = norm(d)
    kn = {norm(k): k for k in known["dept"]}
    if n in kn: return kn[n]
    for c in CANDS.get(n, []):
        if c in known["dept"]: return c
    return d

def canon(v, t): return {k.lower(): k for k in known[t]}.get(v.strip().lower(), v.strip())
def lang_of(n): return "en" if n <= 12 else "ta" if n <= 24 else "ta_rom" if n <= 35 else "hi_rom"

rows = []
for line in DATA.strip().splitlines():
    cid, text, dept, sev, urg = line.split("|")
    alts = [map_dept(d) for d in re.split(r"\s*/\s*", dept)]
    for x in EXTRA_OK.get(cid, []):
        if x in known["dept"] and x not in alts: alts.append(x)
    rows.append({"id": cid, "text": text, "lang": lang_of(int(cid[1:])), "dept": alts[0], "dept_ok": alts,
                 "severity": canon(sev, "severity"), "urgency": canon(urg, "urgency"), "split": "indep"})

with open(OUT, "w", encoding="utf-8") as f:
    for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(f"wrote {len(rows)} rows -> {OUT}")
for lg in ("en", "ta", "ta_rom", "hi_rom"): print(f"  {lg}: {sum(r['lang'] == lg for r in rows)}")
print("synth dept labels:", sorted(known["dept"]))
for t in known:
    bad = sorted({v for r in rows for v in (r["dept_ok"] if t == "dept" else [r[t]]) if v not in known[t]})
    print(f"NOT in synth -> {t}: {bad}")
