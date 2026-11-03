"""Minimal Tamil-script -> plain Latin romanizer, for MATCHING (not display)."""
VOWELS = {"அ": "a", "ஆ": "aa", "இ": "i", "ஈ": "ii", "உ": "u", "ஊ": "uu", "எ": "e", "ஏ": "e",
          "ஐ": "ai", "ஒ": "o", "ஓ": "o", "ஔ": "au"}
SIGNS = {"ா": "aa", "ி": "i", "ீ": "ii", "ு": "u", "ூ": "uu", "ெ": "e", "ே": "e",
         "ை": "ai", "ொ": "o", "ோ": "o", "ௌ": "au"}
CONS = {"க": "k", "ங": "ng", "ச": "s", "ஜ": "j", "ஞ": "ny", "ட": "t", "ண": "n", "த": "t",
        "ந": "n", "ப": "p", "ம": "m", "ய": "y", "ர": "r", "ல": "l", "வ": "v", "ழ": "l",
        "ள": "l", "ற": "r", "ன": "n", "ஷ": "sh", "ஸ": "s", "ஹ": "h"}
PULLI = "்"

# Common civic words -> English (applied before romanizing; longest first)
WORDS = {"திருக்கோயில்": "temple", "கோவில்": "temple", "கோயில்": "temple",
         "பேருந்து நிலையம்": "bus stand", "பேருந்து": "bus", "காவல் நிலையம்": "police station",
         "ரயில் நிலையம்": "railway station", "ரயில்வே": "railway", "ரயில்": "railway",
         "நிலையம்": "stand", "மருத்துவமனை": "hospital", "பள்ளி": "school", "சந்தை": "market",
         "பாலம்": "bridge", "சிக்னல்": "signal", "சாலை": "road", "தெரு": "street", "நகர்": "nagar",
         "பூங்கா": "park", "கடற்கரை": "beach", "கலங்கரை விளக்கம்": "lighthouse", "குளம்": "tank"}
_WORDS_SORTED = sorted(WORDS.items(), key=lambda kv: -len(kv[0]))

import re
_WORD_RES = [(re.compile("(?<![\u0b80-\u0bff])" + re.escape(ta)), en) for ta, en in _WORDS_SORTED]

def has_tamil(s):
    return any("\u0b80" <= ch <= "\u0bff" for ch in s)

def romanize(text):
    for rx, en in _WORD_RES:
        text = rx.sub(f" {en} ", text)
    out, i = [], 0
    while i < len(text):
        c = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if c in CONS:
            if nxt == PULLI:   out.append(CONS[c]); i += 2
            elif nxt in SIGNS: out.append(CONS[c] + SIGNS[nxt]); i += 2
            else:              out.append(CONS[c] + "a"); i += 1
        elif c in VOWELS: out.append(VOWELS[c]); i += 1
        elif c == "ஃ":    out.append("h"); i += 1
        else:             out.append(c); i += 1
    return "".join(out)
