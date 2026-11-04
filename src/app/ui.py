import re, time
import gradio as gr
from src.app import pipeline, tracker

CSS = """
.gradio-container, .gradio-container *:not(h1):not(h2):not(h3) { font-size: 19px !important; font-weight: 600 !important; }
.gradio-container h1 { font-size: 40px !important; font-weight: 800 !important; }
.gradio-container h2, .gradio-container h3 { font-size: 28px !important; font-weight: 800 !important; }
.gradio-container button { font-weight: 700 !important; }
"""

EXAMPLES = [
    "Enga area la rendu naala water varala. Tanker kooda innum anuppala.",
    "எங்கள் பகுதியில் கடந்த மூன்று நாட்களாக குடிநீர் வரவில்லை. அதிகாரிகளிடம் புகார் கொடுத்தும் எந்த நடவடிக்கையும் எடுக்கவில்லை.",
    "Sadak par bahut bade gaddhe hain. Kal ek bike wala gir gaya tha aur use chot bhi lagi.",
    "An exposed electrical wire is hanging dangerously low near a crowded bus stop. Someone could get electrocuted.",
    "Pata nahi kya problem hai, lekin hamare yahan sab kuch pehle se zyada kharab ho gaya hai.",
    "status GRV-000001",
]

def chat(msg, history):
    m = re.match(r"\s*status\s+(GRV-\d+)", msg, re.I)
    if m:
        g = tracker.get(m.group(1))
        if not g: return "I couldn't find that ticket number."
        t, h = g
        due = time.strftime("%d %b %Y %H:%M", time.localtime(t["due"]))
        return f"Ticket {t['id']}: {t['status']}\nDepartment: {t['dept']}\nTarget resolution: {due}\nLatest: {h[-1]['note'] or h[-1]['status']}"
    r = pipeline.handle(msg)
    extra = f"\n\nA similar complaint ({r['parent']}) is already open; yours is linked to it." if r["parent"] else ""
    return r["reply"] + extra

def update(tid, status, note):
    ok = tracker.set_status(tid.strip(), status, note)
    return ("Updated." if ok else "Ticket not found."), tracker.table()

def escalate():
    ids = tracker.escalate_overdue()
    return f"Escalated: {', '.join(ids) or 'none'}", tracker.table()

with gr.Blocks(title="Citizen Grievance Bot") as demo:
    gr.Markdown("# Multilingual Citizen Grievance Chatbot\n**HI-02** | Tamil, Hindi, English, Tanglish and Hinglish | routing, tracking and escalation")
    with gr.Tab("Citizen chat"):
        gr.Markdown("### Type a complaint in any supported language. Send `status GRV-000001` to track a ticket.")
        gr.ChatInterface(chat, examples=EXAMPLES, cache_examples=False)
    with gr.Tab("Officer console"):
        gr.Markdown("### Ticket queue (SLA due time, duplicates, status)")
        table = gr.Dataframe(value=tracker.table, headers=tracker.HEADERS, interactive=False, wrap=True)
        msg = gr.Textbox(label="Result", interactive=False)
        with gr.Row():
            tid = gr.Textbox(label="Ticket id (e.g. GRV-000001)")
            st = gr.Dropdown(tracker.FLOW, value="In Progress", label="New status")
            note = gr.Textbox(label="Note")
        with gr.Row():
            gr.Button("Update").click(update, [tid, st, note], [msg, table])
            gr.Button("Escalate overdue (SLA)").click(escalate, None, [msg, table])
            gr.Button("Refresh").click(tracker.table, None, table)

if __name__ == "__main__":
    try:
        demo.launch(theme=gr.themes.Soft(primary_hue="blue", text_size="lg"), css=CSS)
    except TypeError:
        demo.launch()
