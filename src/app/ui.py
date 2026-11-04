import re, time
import gradio as gr
from src.app import pipeline, tracker

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
    with gr.Tab("Citizen chat"):
        gr.Markdown("Type a complaint in English, Tamil, Tanglish or Hinglish. Send `status GRV-000001` to track a ticket.")
        gr.ChatInterface(chat)
    with gr.Tab("Officer console"):
        table = gr.Dataframe(value=tracker.table, headers=tracker.HEADERS, interactive=False)
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
    demo.launch()
