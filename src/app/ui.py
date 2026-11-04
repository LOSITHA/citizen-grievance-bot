import re, time
import gradio as gr
from src.app import pipeline, tracker

pretty = getattr(pipeline, "pretty", str)

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

:root, .dark, .gradio-container {
  --ink: #3B1A28;
  --body-background-fill: #F2DACE;
  --background-fill-primary: rgba(255,255,255,0.62);
  --background-fill-secondary: rgba(255,255,255,0.45);
  --block-background-fill: rgba(255,255,255,0.62);
  --panel-background-fill: rgba(255,255,255,0.62);
  --block-border-color: #D49A9A;
  --border-color-primary: #D49A9A;
  --block-radius: 14px;
  --block-shadow: 0 2px 10px rgba(124,14,68,0.07);
  --body-text-color: #3B1A28;
  --body-text-color-subdued: #7A4A5E;
  --block-label-text-color: #7C0E44;
  --block-title-text-color: #7C0E44;
  --block-label-background-fill: transparent;
  --input-background-fill: #FFFFFF;
  --input-background-fill-focus: #FFFFFF;
  --input-border-color: #D49A9A;
  --input-border-color-focus: #AA5E7A;
  --input-placeholder-color: #A98593;
  --button-primary-background-fill: #AA5E7A;
  --button-primary-background-fill-hover: #7C0E44;
  --button-primary-text-color: #FFFFFF;
  --button-primary-border-color: #AA5E7A;
  --button-secondary-background-fill: #D49A9A;
  --button-secondary-background-fill-hover: #C58585;
  --button-secondary-text-color: #5A0B30;
  --button-secondary-border-color: #D49A9A;
  --color-accent: #AA5E7A;
  --color-accent-soft: #F2DACE;
  --link-text-color: #7C0E44;
  --table-even-background-fill: #FFFFFF;
  --table-odd-background-fill: #FBEFE9;
  --table-border-color: #E9C7C1;
  --text-sm: 13px;
  --text-md: 15px;
  --text-lg: 16px;
}

body, .gradio-container, .dark body {
  background: #F2DACE !important;
  font-family: 'Inter', 'Segoe UI', 'Nirmala UI', 'Noto Sans Tamil', 'Noto Sans Devanagari', sans-serif !important;
  font-size: 15px;
  font-weight: 400;
  color: #3B1A28;
}
.gradio-container { max-width: 980px !important; margin: 0 auto !important; }
footer { display: none !important; }

.hero {
  background: linear-gradient(120deg, #AA5E7A 0%, #7C0E44 100%);
  border-radius: 18px; padding: 22px 26px; margin: 10px 0 14px; color: #F2DACE;
  box-shadow: 0 6px 18px rgba(124,14,68,0.18);
}
.hero-title { font-size: 25px; font-weight: 600; letter-spacing: 0.2px; color: #F2DACE; }
.hero-sub { font-size: 14px; margin-top: 4px; opacity: 0.92; color: #F2DACE; }
.chips { margin-top: 12px; display: flex; gap: 8px; flex-wrap: wrap; }
.chips span {
  background: rgba(242,218,206,0.16); border: 1px solid rgba(242,218,206,0.45);
  color: #F2DACE; padding: 3px 12px; border-radius: 999px; font-size: 12px; font-weight: 500;
}

.gradio-container h3 { font-size: 16px; font-weight: 600; color: #7C0E44; margin: 4px 0 6px; }
.gradio-container .prose, .gradio-container .prose p, .gradio-container label span { font-size: 14px; font-weight: 400; }
.gradio-container label span { color: #7C0E44; font-weight: 500; }
.gradio-container button { font-size: 14px !important; font-weight: 500 !important; border-radius: 10px !important; }

button[role="tab"] { font-size: 14px !important; font-weight: 500 !important; color: #7A4A5E !important; }
button[role="tab"][aria-selected="true"] { color: #7C0E44 !important; border-bottom: 2px solid #AA5E7A !important; }

.message.user, [data-testid="user"] { background: #AA5E7A !important; color: #FFFFFF !important; border: none !important; border-radius: 14px !important; }
.message.bot, [data-testid="bot"] { background: #FFFFFF !important; color: #3B1A28 !important; border: 1px solid #D49A9A !important; border-radius: 14px !important; }
.message.user *, [data-testid="user"] * { color: #FFFFFF !important; }
.message { font-size: 14.5px !important; line-height: 1.5 !important; }

.gradio-container .examples button, .gradio-container button.example, .gradio-container .example {
  background: #FFFFFF !important; color: #7C0E44 !important; border: 1px solid #D49A9A !important;
  font-size: 13px !important; font-weight: 400 !important; text-align: left !important;
}
.gradio-container .examples button:hover, .gradio-container button.example:hover { background: #F2DACE !important; }

table { font-size: 13.5px !important; }
table th { background: #AA5E7A !important; color: #FFFFFF !important; font-weight: 500 !important; }
textarea, input { font-size: 14px !important; }
"""

HERO = """
<div class="hero">
  <div class="hero-title">Multilingual Citizen Grievance Chatbot</div>
  <div class="hero-sub">Raise a complaint in your own language. It is routed to the right department, tracked and escalated if it is delayed.</div>
  <div class="chips"><span>English</span><span>Tamil</span><span>Hindi</span><span>Tanglish</span><span>Hinglish</span></div>
</div>
"""

EXAMPLES = [
    "Enga area la rendu naala water varala. Tanker kooda innum anuppala.",
    "எங்கள் பகுதியில் கடந்த மூன்று நாட்களாக குடிநீர் வரவில்லை. அதிகாரிகளிடம் புகார் கொடுத்தும் எந்த நடவடிக்கையும் எடுக்கவில்லை.",
    "Sadak par bahut bade gaddhe hain. Kal ek bike wala gir gaya tha aur use chot bhi lagi.",
    "An exposed electrical wire is hanging dangerously low near a crowded bus stop. Someone could get electrocuted.",
    "Pata nahi kya problem hai, lekin hamare yahan sab kuch pehle se zyada kharab ho gaya hai.",
    "status GRV-000001",
]

def rows():
    out = tracker.table()
    for r in out: r[2] = pretty(r[2])
    return out

def chat(msg, history):
    m = re.match(r"\s*status\s+(GRV-\d+)", msg, re.I)
    if m:
        g = tracker.get(m.group(1))
        if not g: return "I couldn't find that ticket number."
        t, h = g
        due = time.strftime("%d %b %Y %H:%M", time.localtime(t["due"]))
        return f"Ticket {t['id']}: {t['status']}\nDepartment: {pretty(t['dept'])}\nTarget resolution: {due}\nLatest: {h[-1]['note'] or h[-1]['status']}"
    r = pipeline.handle(msg)
    extra = f"\n\nA similar complaint ({r['parent']}) is already open; yours is linked to it." if r["parent"] else ""
    return r["reply"] + extra

def update(tid, status, note):
    ok = tracker.set_status(tid.strip(), status, note)
    return ("Updated." if ok else "Ticket not found."), rows()

def escalate():
    ids = tracker.escalate_overdue()
    return f"Escalated: {', '.join(ids) or 'none'}", rows()

with gr.Blocks(title="Citizen Grievance Bot") as demo:
    gr.HTML(HERO)
    with gr.Tab("Citizen chat"):
        gr.Markdown("### Describe your problem in any supported language\nSend `status GRV-000001` to check a ticket.")
        gr.ChatInterface(chat, examples=EXAMPLES, cache_examples=False)
    with gr.Tab("Officer console"):
        gr.Markdown("### Ticket queue\nSLA due time, duplicate links and current status.")
        table = gr.Dataframe(value=rows, headers=tracker.HEADERS, interactive=False, wrap=True)
        msg = gr.Textbox(label="Result", interactive=False)
        with gr.Row():
            tid = gr.Textbox(label="Ticket id (e.g. GRV-000001)")
            st = gr.Dropdown(tracker.FLOW, value="In Progress", label="New status")
            note = gr.Textbox(label="Note")
        with gr.Row():
            gr.Button("Update", variant="primary").click(update, [tid, st, note], [msg, table])
            gr.Button("Escalate overdue (SLA)").click(escalate, None, [msg, table])
            gr.Button("Refresh").click(rows, None, table)

if __name__ == "__main__":
    try:
        demo.launch(css=CSS)
    except TypeError:
        demo.launch()
