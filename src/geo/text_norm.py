"""Normalise place names so spelling variants collapse to one comparable key."""
import re

TOKEN_MAP = {"koil": "temple", "kovil": "temple", "kovel": "temple", "alayam": "temple",
             "mandir": "temple", "stand": "stop", "terminus": "stop", "terminal": "stop",
             "stn": "station", "rly": "railway", "ngr": "nagar", "nagr": "nagar",
             "hosp": "hospital", "govt": "government"}
_SUBS = [("zh", "l"), ("th", "t"), ("dh", "d"), ("kh", "k"), ("gh", "g"), ("sh", "s"),
         ("ph", "f"), ("w", "v"), ("ee", "i"), ("oo", "u"), ("aa", "a"), ("y", "i")]
_PUNCT = re.compile(r"[.,;:!?()\[\]{}\"'`/\\\-_|]")

def skeleton(text):
    t = _PUNCT.sub(" ", str(text).lower())
    s = "".join(TOKEN_MAP.get(w, w) for w in t.split())
    for a, b in _SUBS:
        s = s.replace(a, b)
    return re.sub(r"(.)\1+", r"\1", s)  # collapse doubled letters

if __name__ == "__main__":
    for a, b in [("Pondy Bazaar", "Pondi Bazar"), ("T. Nagar", "T Nagar"),
                 ("Koyambedu bus stand", "Koyambedu Bus Terminus"), ("Murugan koil", "Murugan Temple")]:
        print(a, "|", b, "->", skeleton(a) == skeleton(b))
