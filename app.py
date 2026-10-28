"""Political Arena - Gradio interface.

Run with:  python app.py
The Groq API key is read on the Python side only (from .env); it is never
sent to the browser.
"""

import os
import tempfile

import gradio as gr

from config import MAX_ROUNDS, MIN_ROUNDS, load_settings
from debate_engine import (
    DebateEngine,
    DebateSession,
    DebateState,
    GroqClient,
    ValidationError,
    create_config,
)
from ui_helpers import (
    CSS,
    DISCLAIMER_HTML,
    HEADER_HTML,
    render_debate,
    render_key_notice,
    render_notice,
    render_status,
)


def _write_transcript(state: DebateState):
    """Save the transcript as a Markdown file for download. Returns a path or None."""
    if state is None or not state.turns:
        return None
    folder = tempfile.mkdtemp(prefix="political_arena_")
    path = os.path.join(folder, "political_arena_transcript.md")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(state.to_markdown())
    return path


def start_debate(country, topic, rounds, context, old_session):
    """Generator: streams the debate into the page one response at a time."""
    # A new debate always replaces (and stops) any earlier one.
    if old_session is not None:
        old_session.request_stop()
    session = DebateSession()

    try:
        config = create_config(country, topic, rounds, context)
    except ValidationError as err:
        yield render_status(None, err.user_message), render_notice("error", err.user_message), None, session
        return

    settings = load_settings()
    if not settings.has_api_key:
        message = "No Groq API key found. Add GROQ_API_KEY to the .env file and try again."
        yield render_status(None, message), render_key_notice(False), None, session
        return

    engine = DebateEngine(
        GroqClient(settings.groq_api_key),
        settings.government_model,
        settings.opposition_model,
    )
    for state in engine.run(config, should_stop=lambda: session.stop_requested):
        session.state = state
        yield render_status(state), render_debate(state), None, session

    yield render_status(session.state), render_debate(session.state), _write_transcript(session.state), session


def stop_debate(session):
    """Stop button: ask the running debate to stop and keep what is finished."""
    if session is None or session.state is None:
        return render_status(None, "There is no debate running."), render_debate(None), None, session
    session.request_stop()
    state = session.state
    if state.status == "running":
        state.status = "stopped"
    return render_status(state), render_debate(state), _write_transcript(state), session


def reset_debate(session):
    """Reset button: stop anything running and clear the screen and inputs."""
    if session is not None:
        session.request_stop()
    return (
        "",
        "",
        4,
        "",
        render_status(None),
        render_debate(None),
        None,
        DebateSession(),
    )


def build_interface() -> gr.Blocks:
    with gr.Blocks(css=CSS, title="Political Arena") as demo:
        gr.HTML(HEADER_HTML)
        key_notice = gr.HTML()

        session = gr.State(None)

        with gr.Row():
            with gr.Column(scale=2):
                country = gr.Textbox(label="Country", placeholder="e.g. Egypt", max_lines=1)
                topic = gr.Textbox(
                    label="Debate topic",
                    placeholder="e.g. Should Egypt increase investment in renewable energy?",
                    lines=2,
                )
                rounds = gr.Slider(
                    MIN_ROUNDS, MAX_ROUNDS, value=4, step=1,
                    label=f"Number of rounds ({MIN_ROUNDS}-{MAX_ROUNDS}; 1 round = Government + Opposition)",
                )
                context = gr.Textbox(
                    label="Background context (optional)",
                    placeholder="Any facts, recent events or constraints the debaters should consider.",
                    lines=3,
                )
                with gr.Row():
                    start_btn = gr.Button("Start Debate", elem_id="start-btn")
                    stop_btn = gr.Button("Stop Debate", elem_id="stop-btn")
                    reset_btn = gr.Button("New Debate / Reset", elem_id="reset-btn")
                gr.Examples(
                    examples=[["Egypt", "Should Egypt increase investment in renewable energy?", 4, ""]],
                    inputs=[country, topic, rounds, context],
                    label="Example",
                )
            with gr.Column(scale=3):
                status = gr.HTML(render_status(None))
                debate = gr.HTML(render_debate(None))
                transcript = gr.File(label="Download transcript (Markdown)", interactive=False)

        gr.HTML(DISCLAIMER_HTML)

        outputs = [status, debate, transcript, session]
        start_event = start_btn.click(
            start_debate, inputs=[country, topic, rounds, context, session], outputs=outputs
        )
        # `cancels` interrupts the running generator; the session flag stops it
        # before the next API call.
        stop_btn.click(stop_debate, inputs=[session], outputs=outputs, cancels=[start_event])
        reset_btn.click(
            reset_debate,
            inputs=[session],
            outputs=[country, topic, rounds, context, status, debate, transcript, session],
            cancels=[start_event],
        )
        demo.load(lambda: render_key_notice(load_settings().has_api_key), outputs=key_notice)
    return demo


if __name__ == "__main__":
    build_interface().queue().launch()
