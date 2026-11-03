"""Normalise place names so spelling variants collapse to one comparable key."""
import re
from src.geo.tamil_roman import romanize, has_tamil

TOKEN_MAP = {"koil": "temple", "kovil": "temple", "kovel": "temple", "koyil": "temple",
             "alayam": "temple", "mandir": "temple",
             "stand": "stn", "stop": "stn", "terminus": "stn", "terminal": "stn",
             "station": "stn", "rly": "railway", "ngr": "nagar", "nagr": "nagar",
             "hosp": "hospital", "govt": "government"}
_SUBS = [("zh", "l"), ("th", "t"), ("dh", "d"), ("kh", "k"), ("gh", "g"), ("sh", "s"),
         ("ph", "f"), ("w", "v"), ("ee", "i"), ("oo", "u"), ("aa", "a"), ("y", "i")]
_PUNCT = re.compile(r"[.,;:!?()\[\]{}\"'`/\\\-_|]")

def _collapse(s):
    return re.sub(r"(.)\1+", r"\1", s)

def skeleton(text):
    t = str(text).lower()
    if has_tamil(t):
        t = romanize(t)
    t = _PUNCT.sub(" ", t)
    s = "".join(TOKEN_MAP.get(_collapse(w), w) for w in t.split())
    for a, b in _SUBS:
        s = s.replace(a, b)
    return _collapse(s)

def tokens(text):
    t = str(text).lower()
    if has_tamil(t):
        t = romanize(t)
    out = []
    for w in _PUNCT.sub(" ", t).split():
        w = TOKEN_MAP.get(_collapse(w), w)
        for a, b in _SUBS:
            w = w.replace(a, b)
        out.append(_collapse(w))
    return out

if __name__ == "__main__":
    for a, b in [("Pondy Bazaar", "Pondi Bazar"), ("T. Nagar", "T Nagar"),
                 ("Koyambedu bus stand", "Koyambedu Bus Terminus"), ("Murugan koil", "Murugan Temple")]:
        print(a, "|", b, "->", skeleton(a) == skeleton(b))
