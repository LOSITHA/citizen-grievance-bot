import re
import joblib
from src.app import tracker

MODELS = joblib.load("models/baseline.joblib")
THRESH = 0.50   # auto-route only if department confidence >= this; set it using the Step 14 sweep

TAMIL, DEVA = re.compile(r"[\u0b80-\u0bff]"), re.compile(r"[\u0900-\u097f]")
TA_ROM = {"enga", "illa", "romba", "irukku", "irukkaanga", "panna", "pannunga", "varala", "veetukulla", "aachu", "naala",
          "innum", "nanga", "kooda", "vandhu", "vandhuduchu", "mosama", "edho", "inga", "yaar", "podraanga", "mudiyala", "seekiram"}
HI_ROM = {"hai", "nahi", "nahin", "mein", "hamare", "hamara", "kai", "bahut", "raha", "rahi", "koi", "bhi", "aur", "ka", "ke",
          "ki", "se", "par", "pata", "kya", "kal", "roz", "hain", "tha", "gaya"}

REPLY = {
    "en": "Your complaint is registered. Ticket: {id}. Department: {dept}. Send 'status {id}' any time to check progress.",
    "ta": "உங்கள் புகார் பதிவு செய்யப்பட்டது. டிக்கெட் எண்: {id}. துறை: {dept}. நிலை அறிய 'status {id}' என்று அனுப்பவும்.",
    "ta_rom": "Unga complaint register aayiduchu. Ticket: {id}. Department: {dept}. 'status {id}' nu type panni status paarunga.",
    "hi_rom": "Aapki shikayat darj ho gayi hai. Ticket: {id}. Vibhag: {dept}. Status jaanne ke liye 'status {id}' bhejein.",
    "hi": "आपकी शिकायत दर्ज हो गई है। टिकट: {id}। विभाग: {dept}। स्थिति जानने के लिए 'status {id}' भेजें।",
}
CLARIFY = {
    "en": "I couldn't tell what this is about. Could you tell me where it is and what exactly is wrong? (Ticket {id} is open for a human officer.)",
    "ta": "இது எதைப் பற்றியது என்று புரியவில்லை. எந்த இடத்தில், என்ன பிரச்சனை என்று சொல்ல முடியுமா? (டிக்கெட் {id})",
    "ta_rom": "Idhu enna problem nu puriyala. Enga, enna issue nu konjam sollunga? (Ticket {id})",
    "hi_rom": "Mujhe samajh nahi aaya ki problem kya hai. Kahan aur kya dikkat hai, thoda batayein? (Ticket {id})",
    "hi": "मुझे समझ नहीं आया कि समस्या क्या है। कहाँ और क्या दिक्कत है, कृपया बताएँ। (टिकट {id})",
}

NICE = {"food_civil_supplies": "Food and Civil Supplies", "sewerage_drainage": "Sewerage and Drainage", "solid_waste": "Solid Waste", "animal_control": "Animal Control", "street_lights": "Street Lights"}
def pretty(d):
    return NICE.get(d, d.replace("_", " ").title())

RANK = ["low", "medium", "high", "critical"]
SAFETY_TOKENS = {"spark", "sparks", "smoke", "electrocuted", "electrocute", "manhole", "bite", "bitten", "fire",
                 "ambulance", "accident", "gir", "chot"}
SAFETY_TA = ("கடித்த", "ஆம்புலன்ஸ்")

def safety_override(text, sev, urg):
    """Life-risk wording forces at least 'high' severity and 'immediate' urgency."""
    w = set(re.findall(r"[a-z]+", text.lower()))
    if (w & SAFETY_TOKENS) or any(x in text for x in SAFETY_TA):
        if sev in RANK and RANK.index(sev) < RANK.index("high"): sev = "high"
        return sev, "immediate", True
    return sev, urg, False

def detect_lang(t):
    if TAMIL.search(t): return "ta"
    if DEVA.search(t): return "hi"
    w = set(re.findall(r"[a-z]+", t.lower()))
    a, b = len(w & TA_ROM), len(w & HI_ROM)
    if max(a, b) < 2: return "en"
    return "ta_rom" if a > b else "hi_rom"

def locate(text):
    """TODO (Step 15): call your ward matcher here and return a ward id, or None."""
    return None

def explain(text, dept, k=3):
    m = MODELS["dept"]; feats, clf = m[0], m[-1]
    x = feats.transform([text])
    contrib = x.multiply(clf.coef_[list(clf.classes_).index(dept)]).toarray()[0]
    names = feats.get_feature_names_out()
    return [names[i].split("__", 1)[-1].strip() for i in contrib.argsort()[::-1][:k] if contrib[i] > 0]

def handle(text):
    lang, out, conf = detect_lang(text), {}, {}
    for t, m in MODELS.items():
        P = m.predict_proba([text])[0]; i = P.argmax()
        out[t], conf[t] = m.classes_[i], float(P[i])
    out["severity"], out["urgency"], flagged = safety_override(text, out["severity"], out["urgency"])
    dept = out["dept"] if conf["dept"] >= THRESH else "Unclassified"
    why = explain(text, out["dept"]) if dept != "Unclassified" else []
    if flagged: why = why + ["SAFETY-KEYWORD"]
    tid, parent = tracker.create(text, lang, dept, out["severity"], out["urgency"], conf["dept"], locate(text), ", ".join(why))
    tpl = CLARIFY if dept == "Unclassified" else REPLY
    return {"ticket": tid, "lang": lang, "dept": dept, "severity": out["severity"], "urgency": out["urgency"],
            "confidence": round(conf["dept"], 2), "why": why, "parent": parent, "reply": tpl[lang].format(id=tid, dept=pretty(dept))}



