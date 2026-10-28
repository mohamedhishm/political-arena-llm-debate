# Political Arena — AI Government vs Opposition

**Evidence-Based Political Debate.** A Gradio web app where two separate Groq-hosted LLMs debate a topic you choose: one defends the government of a country, the other acts as the political opposition.

## 1. Project overview

You enter a country, a debate topic, a number of rounds (1–10) and optional background context. The app then alternates between the **Government LLM** and the **Opposition LLM**, showing each argument live as a separate entry. When the debate ends you can download the transcript as a Markdown file.

## 2. Assignment requirements satisfied

| Requirement | Where |
|---|---|
| Two separate LLMs (government / opposition) | Two configurable models, two system prompts (`debate_engine.py`) |
| User chooses country and topic | Inputs in `app.py` |
| Reasoned arguments with data and source attribution | System prompts ask for statistics, source organization and year |
| Free Groq-hosted models | Groq SDK, models set in `.env` |
| Gradio UI | `app.py` + custom CSS in `ui_helpers.py` |
| Maximum 10 rounds | `validate_rounds()` rejects values outside 1–10 |
| Ready for manual GitHub upload | `.gitignore`, `.env.example`, CI workflow |
| API key never exposed | Read from `.env` on the Python side only |

## 3. Features

- Government and Opposition alternate: 1 round = 2 responses (max 10 rounds = 20 responses).
- Conversation history is passed to each model so it answers the other side's actual points.
- Live streaming of each response into the page, with status and round progress.
- **Stop Debate** and **New Debate / Reset** buttons that really stop the running debate (Gradio event cancellation plus a stop flag checked before every API call).
- Finished responses are kept if an API call fails; a failed or empty response is never counted as a turn.
- Friendly messages for a missing key, invalid key, invalid model name, rate limits, network errors and timeouts. No automatic retries.
- Downloadable Markdown transcript and a visible disclaimer.
- Burgundy `#800020` / Beige `#F5E6CC` / Navy `#14213D` design.

## 4. Architecture and folder structure

```
assiment1/
    app.py                  Gradio UI and button handlers
    debate_engine.py        Validation, prompts, Groq wrapper, round loop (no Gradio)
    config.py               Settings loaded from .env, defaults, limits
    ui_helpers.py           CSS and HTML rendering (no Gradio)
    requirements.txt
    README.md
    .env.example            Placeholder settings (safe to commit)
    .gitignore
    tests/
        __init__.py
        test_debate_engine.py
    .github/workflows/tests.yml
```

`.env` is your private local file and is not committed.

## 5. The two LLM roles

- **Government LLM** — defends government policy with logical arguments, statistics and evidence; discusses achievements, objectives, indicators, trade-offs and limitations.
- **Opposition LLM** — challenges the policy with evidence-based criticism: weaknesses, implementation problems, risks, inequalities and alternative policies.

Both must be respectful, answer the other side's real arguments, separate facts from opinions and estimates, name sources and years only when known, admit uncertainty, and never invent statistics, studies or URLs. They are two separate API calls (by default to two different models), not one model playing both parts. Your inputs are placed in the user message inside a delimited block and the system prompt tells the models to treat it as data, so user text cannot replace the role instructions.

## 6. How rounds work

1. Round 1: Government opening statement, then Opposition response.
2. Each later round: Government answers the Opposition's last points, then the Opposition answers the Government.
3. The final round asks for closing statements.
4. The debate stops automatically after the chosen number of rounds. Values below 1 or above 10 are rejected with a message (the Slider also limits the range).

## 7. Statistical verification limitations

A prompt cannot guarantee correct statistics. The models have **no internet access**, and this app does **not** verify any figure. Numbers, studies and sources they cite may be wrong, outdated or invented despite the instructions. Check every statistic against the original source (World Bank, IMF, UN agencies, national statistics offices, official reports). The interface and every transcript contain this disclaimer.

## 8. Prerequisites

- Windows with Python 3.10 or newer (`python --version`)
- A free Groq account and API key
- Internet access

## 9. Windows installation

Open PowerShell in the project folder:

```powershell
cd "C:\Users\msi\OneDrive - Arab Academy for Science and Technology\Desktop\desktop\term7\PT AI2\assiment1"
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then activate again.

## 10. Getting a Groq API key

1. Go to <https://console.groq.com/> and sign in.
2. Open **API Keys** and click **Create API Key**.
3. Copy the key. Do not share it or paste it into chats, code or screenshots.

## 11. Configuring `.env`

Open `.env` in a text editor and fill in the key:

```
GROQ_API_KEY=paste_your_key_here
GOVERNMENT_MODEL=
OPPOSITION_MODEL=
```

Leave the model lines empty to use the defaults (`llama-3.3-70b-versatile` for Government, `llama-3.1-8b-instant` for Opposition), or write any model ID from the Groq console. Values in `.env` are re-read each time you press Start Debate. A non-empty value in `.env` takes priority over a same-named system environment variable.

## 12–13. Install and run

```powershell
pip install -r requirements.txt
python app.py
```

Open the local address printed in the terminal (normally http://127.0.0.1:7860).

## 14. Running tests

```powershell
pytest -q
```

Tests mock the Groq client, so no API key or credits are needed. They cover round limits, turn order, maximum rounds, stopping, history and roles, prompt-injection separation, missing key, API failures, error mapping, reset behavior and HTML escaping.

## 15. Example input

- Country: `Egypt`
- Topic: `Should Egypt increase investment in renewable energy?`
- Rounds: `4` (8 responses)
- Context: *(optional)* `Focus on solar and wind projects and electricity costs.`

## 16. API-key security

- The key lives only in `.env`, which `.gitignore` excludes. Never rename it to a tracked file.
- `.env.example` has empty placeholders only.
- The key is used only by the Python backend; it is not placed in the page, logs, error messages or transcripts.
- If you ever commit a key by accident, revoke it in the Groq console and create a new one (deleting the commit is not enough).

Check before uploading:

```powershell
git check-ignore -v .env
git status
```

`.env` should be reported as ignored and must not appear in `git status`.

## 17. Uploading to GitHub (manual)

Create an empty repository on GitHub yourself, then run in the project folder, replacing `YOUR_GITHUB_REPOSITORY_URL` with your own repository URL:

```powershell
git init
git add .
git status
git commit -m "Build AI political debate application"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

Read the `git status` output before committing and confirm `.env` is not listed.

## 18. Known limitations

- Groq's free tier has rate and token limits; long debates with the larger model may hit them. The app reports the error and keeps finished responses; wait and try again or use fewer rounds.
- Model names change. If you see a model error, update `GOVERNMENT_MODEL` / `OPPOSITION_MODEL` in `.env`.
- Responses are limited to about 700 tokens each to save quota.
- Statistics are not verified (see section 7).
- Stopping while a response is being generated discards that unfinished response.
- `requirements.txt` limits Gradio to versions below 6.
