import os, sqlite3, time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DB = "data/tracker.db"
FLOW = ["Received", "Routed", "Needs Triage", "In Progress", "Resolved", "Escalated"]
SLA_H = {"critical": 4, "high": 24, "medium": 72, "low": 168}
SCALE = float(os.environ.get("SLA_SCALE", "1"))   # set SLA_SCALE=0.0001 to demo escalation quickly
HEADERS = ["Ticket", "Status", "Department", "Severity", "Urgency", "Due", "Duplicate of", "Duplicates"]

def _c():
    os.makedirs("data", exist_ok=True)
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
    return c

def init():
    with _c() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS tickets(id TEXT PRIMARY KEY, created REAL, text TEXT, lang TEXT, dept TEXT,
            severity TEXT, urgency TEXT, ward TEXT, status TEXT, due REAL, confidence REAL, parent_id TEXT, why TEXT, updated REAL);
        CREATE TABLE IF NOT EXISTS history(ticket_id TEXT, ts REAL, status TEXT, note TEXT);""")

def find_similar(text, dept, ward=None, thr=0.55):
    q, args = "SELECT id, text FROM tickets WHERE dept=? AND status!='Resolved' AND parent_id IS NULL", [dept]
    if ward: q += " AND ward=?"; args.append(ward)
    with _c() as c: rows = c.execute(q, args).fetchall()
    if not rows: return None
    v = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4)).fit([r["text"] for r in rows] + [text])
    sims = cosine_similarity(v.transform([text]), v.transform([r["text"] for r in rows]))[0]
    j = int(sims.argmax())
    return rows[j]["id"] if sims[j] >= thr else None

def create(text, lang, dept, severity, urgency, conf, ward=None, why=""):
    init()
    parent = find_similar(text, dept, ward) if dept != "Unclassified" else None
    now = time.time()
    hrs = SLA_H.get(severity.lower(), 72)
    if urgency.lower() in ("immediate", "urgent"): hrs = min(hrs, 6)
    status = "Needs Triage" if dept == "Unclassified" else "Routed"
    with _c() as c:
        tid = f"GRV-{c.execute('SELECT COUNT(*) FROM tickets').fetchone()[0] + 1:06d}"
        c.execute("INSERT INTO tickets VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                  (tid, now, text, lang, dept, severity, urgency, ward, status, now + hrs * 3600 * SCALE, conf, parent, why, now))
        c.execute("INSERT INTO history VALUES (?,?,?,?)", (tid, now, status, "auto-routed" + (f"; duplicate of {parent}" if parent else "")))
    return tid, parent

def get(tid):
    init()
    with _c() as c:
        r = c.execute("SELECT * FROM tickets WHERE id=?", (tid.upper(),)).fetchone()
        if not r: return None
        h = c.execute("SELECT ts, status, note FROM history WHERE ticket_id=? ORDER BY ts", (tid.upper(),)).fetchall()
    return dict(r), [dict(x) for x in h]

def set_status(tid, status, note=""):
    init()
    if status not in FLOW: return False
    now = time.time()
    with _c() as c:
        if not c.execute("SELECT 1 FROM tickets WHERE id=?", (tid.upper(),)).fetchone(): return False
        c.execute("UPDATE tickets SET status=?, updated=? WHERE id=?", (status, now, tid.upper()))
        c.execute("INSERT INTO history VALUES (?,?,?,?)", (tid.upper(), now, status, note))
    return True

def escalate_overdue():
    init(); now = time.time()
    with _c() as c:
        ids = [r["id"] for r in c.execute("SELECT id FROM tickets WHERE due < ? AND status IN ('Received','Routed','Needs Triage','In Progress')", (now,)).fetchall()]
        for i in ids:
            c.execute("UPDATE tickets SET status='Escalated', updated=? WHERE id=?", (now, i))
            c.execute("INSERT INTO history VALUES (?,?,?,?)", (i, now, "Escalated", "SLA breached"))
    return ids

def table(limit=100):
    init()
    with _c() as c:
        rs = c.execute("""SELECT t.id, t.status, t.dept, t.severity, t.urgency, t.due, t.parent_id,
            (SELECT COUNT(*) FROM tickets d WHERE d.parent_id = t.id) AS dupes
            FROM tickets t ORDER BY t.created DESC LIMIT ?""", (limit,)).fetchall()
    return [[r["id"], r["status"], r["dept"], r["severity"], r["urgency"], time.strftime("%d %b %H:%M", time.localtime(r["due"])), r["parent_id"] or "", r["dupes"]] for r in rs]
