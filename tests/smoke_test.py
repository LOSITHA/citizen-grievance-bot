import os, tempfile
from src.app import tracker, pipeline as p

tracker.DB = os.path.join(tempfile.mkdtemp(), "test.db")   # never touches your real tickets

def test_lang():
    assert p.detect_lang("Enga area la rendu naala water varala") == "ta_rom"
    assert p.detect_lang("Hamare area mein paani nahi aa raha hai") == "hi_rom"
    assert p.detect_lang("எங்கள் பகுதியில் குடிநீர் இல்லை") == "ta"
    assert p.detect_lang("No water since yesterday") == "en"

def test_ticket_flow():
    r = p.handle("Enga area la rendu naala water varala. Tanker kooda innum anuppala.")
    assert r["ticket"].startswith("GRV-")
    assert tracker.set_status(r["ticket"], "In Progress", "tanker sent")
    t, h = tracker.get(r["ticket"])
    assert t["status"] == "In Progress" and h[-1]["note"] == "tanker sent"

def test_safety():
    s, u, f = p.safety_override("manhole is open near our house", "low", "routine")
    assert f and s == "high" and u == "immediate"
    assert not p.safety_override("garbage not collected for days", "low", "routine")[2]

if __name__ == "__main__":
    n = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_"): fn(); n += 1; print("PASS", name)
    print(f"{n} passed")
