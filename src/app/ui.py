import re
import gradio as gr
from src.app import pipeline, tracker, views

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
:root, .dark, .gradio-container {
  --body-background-fill: #F2DACE; --background-fill-primary: rgba(255,255,255,0.62); --background-fill-secondary: rgba(255,255,255,0.45);
  --block-background-fill: rgba(255,255,255,0.62); --panel-background-fill: rgba(255,255,255,0.62);
  --block-border-color: #D49A9A; --border-color-primary: #D49A9A; --block-radius: 14px; --block-shadow: 0 2px 10px rgba(124,14,68,0.07);
  --body-text-color: #3B1A28; --body-text-color-subdued: #7A4A5E; --block-label-text-color: #7C0E44; --block-title-text-color: #7C0E44;
  --block-label-background-fill: transparent; --input-background-fill: #FFFFFF; --input-background-fill-focus: #FFFFFF;
  --input-border-color: #D49A9A; --input-border-color-focus: #AA5E7A; --input-placeholder-color: #A98593;
  --button-primary-background-fill: #AA5E7A; --button-primary-background-fill-hover: #7C0E44; --button-primary-text-color: #FFFFFF; --button-primary-border-color: #AA5E7A;
  --button-secondary-background-fill: #D49A9A; --button-secondary-background-fill-hover: #C58585; --button-secondary-text-color: #5A0B30; --button-secondary-border-color: #D49A9A;
  --color-accent: #AA5E7A; --color-accent-soft: #F2DACE; --link-text-color: #7C0E44;
  --text-sm: 13px; --text-md: 15px; --text-lg: 16px;
}
body, .gradio-container, .dark body { background: #F2DACE !important; font-family: 'Inter','Segoe UI','Nirmala UI','Noto Sans Tamil','Noto Sans Devanagari',sans-serif !important; font-size: 15px; font-weight: 400; color: #3B1A28; }
.gradio-container { max-width: 1040px !important; margin: 0 auto !important; }
footer { display: none !important; }
.hero { background: linear-gradient(120deg, #AA5E7A 0%, #7C0E44 100%); border-radius: 18px; padding: 22px 26px; margin: 10px 0 14px; color: #F2DACE; box-shadow: 0 6px 18px rgba(124,14,68,0.18); }
.hero-title { font-size: 25px; font-weight: 600; color: #F2DACE; }
.hero-sub { font-size: 14px; margin-top: 4px; opacity: 0.92; color: #F2DACE; }
.chips { margin-top: 12px; display: flex; gap: 8px; flex-wrap: wrap; }
.chips span { background: rgba(242,218,206,0.16); border: 1px solid rgba(242,218,206,0.45); color: #F2DACE; padding: 3px 12px; border-radius: 999px; font-size: 12px; font-weight: 500; }
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
textarea, input { font-size: 14px !important; }
textarea::placeholder, input::placeholder { font-style: italic !important; }
.stats { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; margin: 6px 0 12px; }
@media (max-width: 700px) { .stats { grid-template-columns: repeat(3, 1fr); } }
.stat { background: #FFFFFF; border: 1px solid #D49A9A; border-radius: 14px; padding: 12px 8px; text-align: center; }
.stat .n { font-size: 24px; font-weight: 600; color: #7C0E44; line-height: 1.1; }
.stat .l { font-size: 12px; color: #7A4A5E; margin-top: 2px; }
.qwrap { overflow-x: auto; background: #FFFFFF; border: 1px solid #D49A9A; border-radius: 14px; }
table.queue { width: 100%; border-collapse: collapse; font-size: 13.5px; }
table.queue th { background: #AA5E7A; color: #FFFFFF; font-weight: 500; text-align: left; padding: 10px 12px; white-space: nowrap; }
table.queue td { padding: 10px 12px; border-top: 1px solid #F0D9D3; vertical-align: top; color: #3B1A28; }
table.queue tr:nth-child(even) td { background: #FBEFE9; }
td.tid { font-weight: 600; color: #7C0E44; white-space: nowrap; }
td.txt { max-width: 320px; color: #5B3A48; }
td.overdue { color: #7C0E44; font-weight: 600; }
.dup { display: inline-block; background: #F2DACE; color: #7C0E44; border-radius: 999px; padding: 1px 8px; font-size: 11.5px; margin-left: 6px; }
.badge { display: inline-block; padding: 3px 11px; border-radius: 999px; font-size: 12.5px; font-weight: 500; white-space: nowrap; }
.empty { background: #FFFFFF; border: 1px dashed #D49A9A; border-radius: 14px; padding: 22px; text-align: center; color: #7A4A5E; font-style: italic; }
.tcard { background: #FFFFFF; border: 1px solid #D49A9A; border-radius: 16px; padding: 20px 22px; }
.thead { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
.tnum { font-size: 22px; font-weight: 600; color: #7C0E44; }
.steps { display: flex; margin: 18px 0 14px; }
.step { flex: 1; text-align: center; position: relative; }
.step:not(:last-child)::after { content: ""; position: absolute; top: 15px; left: 55%; width: 90%; height: 3px; background: #E9C7C1; }
.step.done:not(:last-child)::after { background: #AA5E7A; }
.dot { width: 32px; height: 32px; line-height: 32px; border-radius: 50%; background: #E9C7C1; color: #7A4A5E; margin: 0 auto; position: relative; z-index: 1; font-size: 13px; }
.step.done .dot { background: #AA5E7A; color: #FFFFFF; }
.step.now .dot { background: #7C0E44; color: #FFFFFF; box-shadow: 0 0 0 4px #F2DACE; }
.step .lbl { font-size: 12.5px; margin-top: 6px; color: #7A4A5E; }
.step.now .lbl, .step.done .lbl { color: #7C0E44; }
.tmsg { background: #F2DACE; border-radius: 12px; padding: 10px 14px; margin: 8px 0 14px; color: #5A0B30; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px 24px; margin: 8px 0 14px; }
.k { font-size: 12px; color: #7A4A5E; }
.v { font-size: 14.5px; color: #3B1A28; }
.reply { border-left: 4px solid #AA5E7A; background: #FBEFE9; padding: 10px 14px; border-radius: 8px; margin: 8px 0 14px; }
.reply .rh { font-weight: 600; color: #7C0E44; font-size: 13px; margin-bottom: 2px; }
.reply.none { color: #7A4A5E; font-style: italic; border-left-color: #D49A9A; }
.when { font-size: 12px; color: #8A6475; }
ul.tl { padding-left: 18px; margin: 6px 0 0; }
ul.tl li { margin-bottom: 5px; font-size: 13.5px; }
.ctext { background: #FBEFE9; border-radius: 10px; padding: 10px 14px; font-size: 14px; color: #3B1A28; margin-top: 2px; }
"""

HERO = """
<div class="hero">
  <div class="hero-title">Multilingual Citizen Grievance Chatbot</div>
  <div class="hero-sub">Raise a complaint in your own language. You get a ticket number, it is routed to the right department, and you can track it until it is resolved.</div>
  <div class="chips"><span>English</span><span>Tamil</span><span>Hindi</span><span>Tanglish</span><span>Hinglish</span></div>
</div>
"""

GREET = {
    "en": "Hello! I can help you register a complaint and track it. Please describe the problem and where it is. You can also send 'status GRV-000001' to check a ticket.",
    "ta": "வணக்கம்! உங்கள் புகாரை பதிவு செய்ய நான் உதவுகிறேன். என்ன பிரச்சனை, எங்கே என்று எழுதுங்கள்.",
    "ta_rom": "Vanakkam! Unga complaint-a register panna naan help panren. Enna problem, enga nu sollunga.",
    "hi_rom": "Namaste! Main aapki shikayat darj karne mein madad karunga. Kya problem hai aur kahan, batayein.",
    "hi": "नमस्ते! मैं आपकी शिकायत दर्ज करने में मदद करूँगा। समस्या क्या है और कहाँ, बताइए।",
}
HELLO = {"hi", "hii", "hiii", "hello", "hey", "helo", "hola", "vanakkam", "vanakam", "namaste", "namaskar", "help", "start",
         "there", "sir", "madam", "good", "morning", "evening", "afternoon", "bot", "வணக்கம்", "नमस्ते", "नमस्कार"}
THANKS = {"thanks", "thank", "you", "thankyou", "thx", "nandri", "dhanyavad", "shukriya", "ok", "okay", "bye", "நன்றி", "धन्यवाद"}

def smalltalk(msg):
    t = [w.strip(" !.?,;:-~") for w in msg.lower().split()]
    t = [w for w in t if w]
    if not t: return "Please write your complaint."
    if set(t) <= HELLO:
        lang = pipeline.detect_lang(msg)
        if set(t) & {"vanakkam", "vanakam"}: lang = "ta_rom"
        elif set(t) & {"namaste", "namaskar"}: lang = "hi_rom"
        return GREET.get(lang, GREET["en"])
    if set(t) <= THANKS:
        return "You are welcome! Write another complaint any time, or send your ticket number to check its status."
    if len(t) < 2: return "Could you tell me a little more? What is the problem and where is it?"
    return None

def chat(msg, history):
    m = re.match(r"^\s*(?:status\s+)?(GRV-\d+)\s*$", msg, re.I)
    if m: return views.chat_card(m.group(1))
    sm = smalltalk(msg)
    if sm: return sm
    r = pipeline.handle(msg)
    out = r["reply"] + "\n\n---\n" + views.chat_card(r["ticket"])
    if r["parent"]: out += f"\n\nA similar complaint ({r['parent']}) is already open; yours is linked to it."
    out += f"\n\n*Check progress any time: type `status {r['ticket']}` here, or open the **Track my complaint** tab.*"
    return out

STATUS_CHOICES = [("Sent to department", "Routed"), ("In progress", "In Progress"), ("Resolved", "Resolved"), ("Escalated", "Escalated")]
FILTER_STATUS = ["All", "Sent to department", "Waiting for officer review", "In progress", "Resolved", "Escalated"]

def refresh_all(fs, fd):
    depts = views.dept_choices()
    fd = fd if fd in depts else "All"
    return views.summary_html(), views.queue_html(fs, fd), gr.update(choices=depts, value=fd), gr.update(choices=views.ticket_ids())

def do_update(tid, status, note, fs, fd):
    if not tid: msg = "Choose a ticket first."
    elif tracker.set_status(tid.strip(), status, (note or "").strip()): msg = f"Ticket {tid} updated. The citizen will see this when they check the ticket."
    else: msg = "Ticket not found."
    return (msg, *refresh_all(fs, fd))

def do_escalate(fs, fd):
    ids = tracker.escalate_overdue()
    msg = f"Escalated: {', '.join(ids)}" if ids else "No overdue tickets right now."
    return (msg, *refresh_all(fs, fd))

with gr.Blocks(title="Citizen Grievance Bot") as demo:
    gr.HTML(HERO)
    with gr.Tab("Citizen chat"):
        gr.Markdown("### Describe your problem in any supported language\nYou will get a ticket number. Keep it to check progress later.")
        bot = gr.Chatbot(placeholder="*Write your complaint here*\n\n*in English, Tamil, Hindi, Tanglish or Hinglish*", height=430)
        box = gr.Textbox(placeholder="Write your complaint here...", container=False, scale=7)
        try:
            gr.ChatInterface(chat, chatbot=bot, textbox=box, save_history=True)
        except TypeError:
            gr.ChatInterface(chat, chatbot=bot, textbox=box)
    with gr.Tab("Track my complaint"):
        gr.Markdown("### Check the status of your complaint\nEnter the ticket number you received, for example GRV-000001.")
        with gr.Row():
            track_id = gr.Textbox(placeholder="GRV-000001", label="Ticket number", scale=4)
            track_btn = gr.Button("Check status", variant="primary", scale=1)
        track_out = gr.HTML()
        track_btn.click(views.ticket_html, track_id, track_out)
        track_id.submit(views.ticket_html, track_id, track_out)
    with gr.Tab("Officer console"):
        gr.Markdown("### Complaint queue\nSee where every complaint was sent, how urgent it is and when it is due.")
        summary = gr.HTML()
        with gr.Row():
            f_status = gr.Dropdown(FILTER_STATUS, value="All", label="Show status")
            f_dept = gr.Dropdown(["All"], value="All", label="Show department")
            refresh = gr.Button("Refresh")
        queue = gr.HTML()
        gr.Markdown("### Update a ticket")
        with gr.Row():
            tid = gr.Dropdown(choices=[], label="Ticket", allow_custom_value=True)
            st = gr.Dropdown(STATUS_CHOICES, value="In Progress", label="New status")
            note = gr.Textbox(label="Message to the citizen (optional)", placeholder="For example: Tanker dispatched, water by 6 PM")
        with gr.Row():
            upd = gr.Button("Update ticket", variant="primary")
            esc_btn = gr.Button("Escalate overdue tickets")
        result = gr.Markdown()
        outs = [summary, queue, f_dept, tid]
        refresh.click(refresh_all, [f_status, f_dept], outs)
        f_status.input(refresh_all, [f_status, f_dept], outs)
        f_dept.input(refresh_all, [f_status, f_dept], outs)
        upd.click(do_update, [tid, st, note, f_status, f_dept], [result] + outs)
        esc_btn.click(do_escalate, [f_status, f_dept], [result] + outs)
    demo.load(refresh_all, [f_status, f_dept], outs)

if __name__ == "__main__":
    try:
        demo.launch(css=CSS)
    except TypeError:
        demo.launch()
