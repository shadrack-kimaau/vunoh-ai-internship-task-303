## Vunoh Global | AI Internship Practical Test

AI-powered Django + vanilla JS web app that helps diaspora customers initiate and track:
- sending money
- hiring local services
- verifying documents
- airport transfers
- checking task status

### Tech stack
- **Backend**: Django
- **Frontend**: HTML + CSS + vanilla JavaScript (no frameworks)
- **Database**: SQLite (persistent `db.sqlite3`)
- **AI brain**: OpenAI-compatible Chat Completions API (configurable)

### Setup (Windows / PowerShell)
Create and activate a virtual environment (optional if you already have `.venv`):

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations and start the server:

```bash
python manage.py migrate
python manage.py runserver
```

Open the app at `http://127.0.0.1:8000/`.

### AI configuration (optional)
If you do **not** set an API key, the app falls back to deterministic heuristics for intent/entities and uses safe fallback generators for steps/messages.

Environment variables:
- **AI_API_KEY** (or **OPENAI_API_KEY**): API key
- **AI_BASE_URL**: OpenAI-compatible base URL (default `https://api.openai.com/v1`)
- **AI_MODEL**: model name (default `gpt-4o-mini`)

### Risk scoring logic (0–100)
Risk is computed deterministically and saved per task. Key factors:
- **Urgency** (“urgent/asap/immediately”): +20 (reduced time for verification)
- **Returning customer history** (completion ratio for `client_id`):
  - > 0.7: −15
  - < 0.3 (and non-zero history): +10
- **Send money**:
  - amount >= 100,000: +30
  - >= 50,000: +20
  - >= 20,000: +10
  - missing amount: +10 (uncertainty)
  - missing recipient name: +15
  - missing location/method details: +10 to +20
- **Verify document**:
  - land title / title deed: +40 (high-impact fraud risk)
  - other docs: +25
  - missing document reference: +10
- **Hire service**:
  - missing schedule date: +20
  - missing service type/location: +10 each
- **Check status**: generally low risk (+5), but missing task code adds uncertainty (+20)

### SQL dump (schema + 5 sample tasks)
This repo includes a repeatable way to generate the required SQL dump:

1) Seed at least five sample tasks (with entities, steps, messages, assignment, risk score):

```bash
python manage.py seed_sample_tasks --min 5
```

2) Export the dump:

```bash
python manage.py export_sql_dump --output sql_dump.sql
```

The generated file will be `sql_dump.sql` at the project root.

### Decisions I made and why
- **AI tools I used**: Used an LLM to help draft the JSON-only prompt formats and to sanity-check example outputs (intent/entities, steps, and channel-specific messages). I kept the app functional without an API key by adding heuristic fallbacks so the project can always run for review.
- **System prompt design**: I constrained outputs to **JSON only**, enumerated **allowed intents**, and required a fixed set of entity keys with `null` for unknowns. This makes parsing predictable and makes downstream risk scoring stable.
- **One decision I overrode**: Instead of “just trust the model output”, I added server-side normalization (e.g., `amount_kes` normalization and SMS length enforcement) and a heuristics fallback. This reduces demo-breaking failures during evaluation.
- **One thing that didn’t work as expected**: Some providers wrap JSON in extra text. I fixed this by extracting the first JSON object from the model output and retrying once with a stricter instruction.



pip install -r requirements.txt
python manage.py migrate
python manage.py seed_sample_tasks --min 5
python manage.py export_sql_dump --output sql_dump.sql
python manage.py runserver

Before you submit (quick checklist)
SQL dump file exists in repo: confirm sql_dump.sql is present (generated via python manage.py export_sql_dump --output sql_dump.sql).
At least 5 sample tasks: run python manage.py seed_sample_tasks --min 5 (you already have 5+ now).
README is complete: includes setup + “Decisions I made and why” (done).
LLM API key (recommended): set AI_API_KEY (or OPENAI_API_KEY) so reviewers see real LLM behavior (intent/steps/messages). Without it, the app still works via fallbacks, but it’s safer to demonstrate the real AI path.
One important note
Your workspace is not currently a git repo, so make sure you initialize git, commit everything (including sql_dump.sql), and push to GitHub before submitting the link.