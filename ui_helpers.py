"""HTML rendering and CSS for the Political Arena interface.

Kept separate from app.py so the layout code stays short and so the
rendering can be tested without Gradio. All model text is HTML-escaped.
"""

import html
import re
from typing import Optional

from debate_engine import DISCLAIMER, GOVERNMENT, SIDE_LABELS, DebateState

BURGUNDY = "#800020"
BEIGE = "#F5E6CC"
NAVY = "#14213D"

HEADER_HTML = """
<div class="arena-header">
  <div class="arena-eyebrow">Evidence-Based Political Debate</div>
  <h1>POLITICAL ARENA</h1>
  <div class="arena-sub">AI Government vs Opposition</div>
  <div class="arena-bar"><span class="bar-gov"></span><span class="bar-opp"></span></div>
</div>
"""

DISCLAIMER_HTML = (
    '<div class="arena-disclaimer"><strong>Disclaimer.</strong> '
    f"{html.escape(DISCLAIMER)}</div>"
)

STATUS_LABELS = {
    "idle": "Ready",
    "running": "Debate in progress",
    "completed": "Debate completed",
    "stopped": "Debate stopped",
    "error": "Debate interrupted",
}


def format_text(text: str) -> str:
    """Escape model text and apply a little formatting (paragraphs, **bold**)."""
    safe = html.escape(text.strip())
    safe = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe)
    paragraphs = [p for p in re.split(r"\n\s*\n", safe) if p.strip()]
    return "".join(f"<p>{p.strip().replace(chr(10), '<br>')}</p>" for p in paragraphs)


def render_notice(kind: str, text: str) -> str:
    """kind: 'error' or 'info'."""
    return f'<div class="arena-notice {kind}">{html.escape(text)}</div>'


def render_key_notice(has_key: bool) -> str:
    if has_key:
        return ""
    return render_notice(
        "error",
        "No Groq API key detected. Open the .env file, add GROQ_API_KEY=your_key, "
        "save it, then click Start Debate.",
    )


def render_status(state: Optional[DebateState], message: str = "") -> str:
    if state is None:
        body = html.escape(message) if message else "Enter a country and topic, then press Start Debate."
        return (
            '<div class="status-card"><span class="pill idle">Ready</span>'
            f'<div class="status-line">{body}</div></div>'
        )

    cfg = state.config
    if state.status == "running":
        speaker = SIDE_LABELS[state.current_side]
        line = f"Round {state.current_round} of {cfg.rounds} - {speaker} is responding..."
    elif state.status == "completed":
        line = f"All {cfg.rounds} rounds finished."
    elif state.status == "stopped":
        line = f"Stopped after {state.completed_rounds} complete round(s). Responses so far are kept."
    else:
        line = state.error

    percent = int(100 * state.response_count / state.max_responses)
    return f"""
<div class="status-card">
  <span class="pill {state.status}">{STATUS_LABELS.get(state.status, state.status)}</span>
  <div class="status-line">{html.escape(line)}</div>
  <div class="meta"><b>Country:</b> {html.escape(cfg.country)} &nbsp;|&nbsp; <b>Topic:</b> {html.escape(cfg.topic)}</div>
  <div class="progress"><div class="progress-fill" style="width:{percent}%"></div></div>
  <div class="progress-text">Completed rounds: {state.completed_rounds} / {cfg.rounds}
    &nbsp;|&nbsp; Responses: {state.response_count} / {state.max_responses}</div>
</div>
"""


def render_debate(state: Optional[DebateState]) -> str:
    if state is None:
        return '<div class="empty-stage">The debate floor is empty. Start a debate to see arguments here.</div>'

    entries = []
    for turn in state.turns:
        css = "gov" if turn.side == GOVERNMENT else "opp"
        entries.append(
            f'<div class="entry {css}"><div class="entry-head">'
            f'<span class="round-tag">Round {turn.round_number}</span>'
            f'<span class="side-name">{SIDE_LABELS[turn.side]}</span></div>'
            f'<div class="entry-body">{format_text(turn.content)}</div></div>'
        )

    if state.status == "running":
        css = "gov" if state.current_side == GOVERNMENT else "opp"
        entries.append(
            f'<div class="entry {css} waiting"><div class="entry-head">'
            f'<span class="round-tag">Round {state.current_round}</span>'
            f'<span class="side-name">{SIDE_LABELS[state.current_side]}</span></div>'
            '<div class="entry-body"><p>Preparing argument...</p></div></div>'
        )
    if state.status == "error":
        entries.append(render_notice("error", state.error + " Completed responses above were preserved."))
    return '<div class="stage">' + "".join(entries) + "</div>"


CSS = f"""
.gradio-container {{ background: {BEIGE} !important; color-scheme: light; max-width: 1200px !important; margin: auto; }}
.gradio-container, .gradio-container label, .gradio-container span, .gradio-container p {{ color: {NAVY}; }}
.arena-header {{ background: linear-gradient(135deg, {NAVY} 0%, #1d2f55 100%); border-bottom: 5px solid {BURGUNDY};
  border-radius: 14px; padding: 28px 20px 18px; text-align: center; margin-bottom: 14px; }}
.arena-header h1 {{ color: {BEIGE} !important; font-family: Georgia, 'Times New Roman', serif; letter-spacing: 8px;
  font-size: 2.6rem; margin: 6px 0; }}
.arena-eyebrow {{ color: #e7c9a0; letter-spacing: 3px; text-transform: uppercase; font-size: .8rem; }}
.arena-sub {{ color: {BEIGE}; font-size: 1.2rem; font-style: italic; }}
.arena-bar {{ display: flex; height: 6px; max-width: 320px; margin: 14px auto 0; border-radius: 3px; overflow: hidden; }}
.arena-bar .bar-gov {{ flex: 1; background: {BURGUNDY}; }}
.arena-bar .bar-opp {{ flex: 1; background: #3b5185; }}
.arena-disclaimer {{ background: #fff8ea; border: 1px solid #d8c29a; border-radius: 10px; padding: 12px 16px;
  font-size: .88rem; color: {NAVY}; margin-top: 14px; }}
.arena-notice {{ border-radius: 10px; padding: 12px 16px; margin: 8px 0; font-size: .95rem; }}
.arena-notice.error {{ background: #fbe9ec; border: 1px solid {BURGUNDY}; color: {BURGUNDY}; }}
.arena-notice.info {{ background: #e8ecf5; border: 1px solid {NAVY}; color: {NAVY}; }}
.status-card {{ background: #fffaf0; border: 1px solid #d8c29a; border-radius: 12px; padding: 14px 18px; }}
.status-line {{ font-weight: 600; margin: 8px 0 4px; color: {NAVY}; }}
.meta {{ font-size: .9rem; color: #3a4466; }}
.pill {{ display: inline-block; padding: 3px 12px; border-radius: 999px; font-size: .78rem; font-weight: 700;
  letter-spacing: 1px; text-transform: uppercase; color: #fff; background: {NAVY}; }}
.pill.running {{ background: {BURGUNDY}; }}
.pill.error {{ background: #a33; }}
.pill.stopped {{ background: #7a6a4f; }}
.progress {{ background: #e6d6b8; border-radius: 6px; height: 10px; margin-top: 10px; overflow: hidden; }}
.progress-fill {{ background: {BURGUNDY}; height: 100%; transition: width .4s ease; }}
.progress-text {{ font-size: .82rem; margin-top: 4px; color: #3a4466; }}
.stage {{ display: flex; flex-direction: column; gap: 14px; }}
.empty-stage {{ text-align: center; padding: 40px 10px; color: #6b6f85; font-style: italic;
  background: #fffaf0; border: 1px dashed #cdb892; border-radius: 12px; }}
.entry {{ background: #fffaf0; border-radius: 12px; padding: 14px 18px; border: 1px solid #e0cfae;
  border-left: 8px solid {BURGUNDY}; box-shadow: 0 2px 6px rgba(20,33,61,.08); }}
.entry.opp {{ border-left-color: {NAVY}; }}
.entry.waiting {{ opacity: .6; font-style: italic; }}
.entry-head {{ display: flex; justify-content: space-between; margin-bottom: 6px; }}
.round-tag {{ font-size: .78rem; letter-spacing: 1px; text-transform: uppercase; color: #6b6f85; font-weight: 700; }}
.entry .side-name {{ font-weight: 800; color: {BURGUNDY}; }}
.entry.opp .side-name {{ color: {NAVY}; }}
.entry-body p {{ color: {NAVY}; line-height: 1.6; margin: 6px 0; font-size: 1rem; }}
#start-btn {{ background: {BURGUNDY} !important; color: {BEIGE} !important; border: none !important; font-weight: 700; }}
#stop-btn {{ background: {NAVY} !important; color: {BEIGE} !important; border: none !important; font-weight: 700; }}
#reset-btn {{ background: transparent !important; color: {NAVY} !important; border: 2px solid {NAVY} !important; font-weight: 700; }}
.gradio-container textarea, .gradio-container input[type=text] {{ background: #fffaf0 !important; color: {NAVY} !important; }}
@media (max-width: 760px) {{ .arena-header h1 {{ font-size: 1.7rem; letter-spacing: 4px; }} }}
"""
