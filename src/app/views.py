import html, time
from src.app import tracker

STEPS = ["Registered", "Sent to department", "In progress", "Resolved"]
STEP_OF = {"Received": 1, "Needs Triage": 1, "Routed": 2, "In Progress": 3, "Escalated": 3, "Resolved": 4}
DISPLAY = {"Received": "Received", "Routed": "Sent to department", "Needs Triage": "Waiting for officer review",
           "In Progress": "In progress", "Resolved": "Resolved", "Escalated": "Escalated"}
BADGE = {"Received": ("#E9C7C1", "#4A1030"), "Routed": ("#D49A9A", "#4A1030"), "Needs Triage": ("#E6D3CC", "#5B4A44"),
         "In Progress": ("#AA5E7A", "#FFFFFF"), "Resolved": ("#5E8C6A", "#FFFFFF"), "Escalated": ("#7C0E44", "#FFFFFF")}
WAITING = ("Received", "Routed", "Needs Triage")
OPEN = ("Received", "Routed", "Needs Triage", "In Progress")

def esc(x): return html.escape(str(x))
def pretty(d): return d.replace("_", " ").title()
def short(d): return "Not assigned" if d == "Unclassified" else pretty(d)
def dept_label(d): return "Not assigned yet (an officer will review it)" if d == "Unclassified" else pretty(d)
def fmt(ts): return time.strftime("%a %d %b, %I:%M %p", time.localtime(ts))

def badge(status):
    bg, fg = BADGE.get(status, ("#D49A9A", "#4A1030"))
    return f'<span class="badge" style="background:{bg};color:{fg}">{esc(DISPLAY.get(status, status))}</span>'

def clean_note(status, note):
    if note.startswith("auto-routed"):
        base = "Registered; an officer will review it" if status == "Needs Triage" else "Registered and sent to the department"
        return base + (" (linked to an earlier similar complaint)" if "duplicate" in note else "")
    if note == "SLA breached": return "Target time passed, escalated to a senior officer"
    return note

def is_dept_message(note): return bool(note) and not note.startswith("auto-routed") and note != "SLA breached"

def _rows():
    tracker.init()
    with tracker._c() as c:
        return [dict(r) for r in c.execute("SELECT * FROM tickets ORDER BY created DESC").fetchall()]

def ticket_ids(): return [r["id"] for r in _rows()]
def dept_choices(): return ["All"] + sorted({short(r["dept"]) for r in _rows()})

def summary_html():
    rs, now = _rows(), time.time()
    cards = [("Total", len(rs)), ("Waiting", sum(r["status"] in WAITING for r in rs)),
             ("In progress", sum(r["status"] == "In Progress" for r in rs)), ("Resolved", sum(r["status"] == "Resolved" for r in rs)),
             ("Escalated", sum(r["status"] == "Escalated" for r in rs)), ("Overdue", sum(r["status"] in OPEN and r["due"] < now for r in rs))]
    return '<div class="stats">' + "".join(f'<div class="stat"><div class="n">{n}</div><div class="l">{l}</div></div>' for l, n in cards) + "</div>"

def queue_html(status="All", dept="All"):
    rs, now = _rows(), time.time()
    if status != "All": rs = [r for r in rs if DISPLAY.get(r["status"], r["status"]) == status]
    if dept != "All": rs = [r for r in rs if short(r["dept"]) == dept]
    if not rs: return '<div class="empty">No tickets to show.</div>'
    body = ""
    for r in rs:
        late = r["due"] < now and r["status"] in OPEN
        dup = f'<span class="dup">linked to {esc(r["parent_id"])}</span>' if r["parent_id"] else ""
        txt = esc(r["text"][:90]) + ("..." if len(r["text"]) > 90 else "")
        body += (f'<tr><td class="tid">{esc(r["id"])}</td><td>{fmt(r["created"])}</td><td>{esc(short(r["dept"]))}</td>'
                 f'<td>{esc(r["severity"].title())} / {esc(r["urgency"].title())}</td><td>{badge(r["status"])}</td>'
                 f'<td class="{"overdue" if late else ""}">{fmt(r["due"])}{" (overdue)" if late else ""}</td><td class="txt">{txt}{dup}</td></tr>')
    return ('<div class="qwrap"><table class="queue"><thead><tr><th>Ticket</th><th>Registered</th><th>Department</th><th>Priority</th>'
            f'<th>Status</th><th>Target by</th><th>Complaint</th></tr></thead><tbody>{body}</tbody></table></div>')

def chat_card(tid):
    g = tracker.get(tid.upper())
    if not g: return "I couldn't find that ticket number. Please check it and try again."
    t, h = g
    lines = [f"**Ticket number: {t['id']}**", f"Department: {dept_label(t['dept'])}",
             f"Priority: {t['severity'].title()} / {t['urgency'].title()}", f"Status: {DISPLAY.get(t['status'], t['status'])}",
             f"Expected resolution by: {fmt(t['due'])}"]
    msgs = [x for x in h if is_dept_message(x["note"])]
    if msgs: lines.append(f"Latest message from the department: {msgs[-1]['note']}")
    return "  \n".join(lines)

STATUS_MSG = {
    "Received": "Your complaint has been received.",
    "Routed": "Your complaint has reached the department and is waiting to be picked up.",
    "Needs Triage": "We could not tell which department this belongs to. An officer will review it and may contact you.",
    "In Progress": "The department is working on your complaint.",
    "Resolved": "The department has marked your complaint as resolved.",
    "Escalated": "This complaint passed its target time, so it was escalated to a senior officer.",
}

def ticket_html(tid):
    tid = (tid or "").strip().upper()
    g = tracker.get(tid) if tid else None
    if not g: return '<div class="empty">No ticket found with that number. Check it and try again, for example GRV-000001.</div>'
    t, hist = g
    step = STEP_OF.get(t["status"], 2)
    steps = ""
    for i, name in enumerate(STEPS, 1):
        cls = "done" if (i < step or t["status"] == "Resolved") else ("now" if i == step else "")
        steps += f'<div class="step {cls}"><div class="dot">{i}</div><div class="lbl">{name}</div></div>'
    msgs = [h for h in hist if is_dept_message(h["note"])]
    if msgs:
        reply = f'<div class="reply"><div class="rh">Latest message from the department</div>{esc(msgs[-1]["note"])}<div class="when">{fmt(msgs[-1]["ts"])}</div></div>'
    else:
        reply = '<div class="reply none">No message from the department yet.</div>'
    tl = "".join(f'<li><span class="when">{fmt(h["ts"])}</span> &nbsp;{esc(DISPLAY.get(h["status"], h["status"]))}: {esc(clean_note(h["status"], h["note"]))}</li>' for h in hist)
    link = f'<div class="when">Linked to ticket {esc(t["parent_id"])} (same issue reported nearby).</div>' if t["parent_id"] else ""
    return (f'<div class="tcard"><div class="thead"><div class="tnum">{esc(t["id"])}</div>{badge(t["status"])}</div>'
            f'<div class="steps">{steps}</div><div class="tmsg">{esc(STATUS_MSG.get(t["status"], ""))}</div>'
            f'<div class="grid2"><div><div class="k">Department</div><div class="v">{esc(dept_label(t["dept"]))}</div></div>'
            f'<div><div class="k">Priority</div><div class="v">{esc(t["severity"].title())} / {esc(t["urgency"].title())}</div></div>'
            f'<div><div class="k">Registered</div><div class="v">{fmt(t["created"])}</div></div>'
            f'<div><div class="k">Expected resolution by</div><div class="v">{fmt(t["due"])}</div></div></div>'
            f'{reply}<div class="k">Your complaint</div><div class="ctext">{esc(t["text"])}</div>{link}'
            f'<div class="k" style="margin-top:12px">Timeline</div><ul class="tl">{tl}</ul></div>')
