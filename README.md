# AI-Powered Diaspora Task Orchestration System
### Vunoh Global | AI Internship Practical Test

This is an AI-powered Django web application that simulates a task orchestration assistant for Kenyans living in the diaspora. It allows users to submit natural language requests and automatically converts them into structured, trackable tasks with AI-driven intent extraction, risk scoring, workflow generation, and multi-channel communication.

The system replaces informal WhatsApp-based coordination with structured, auditable workflows.

---

## Core Features

The system supports the following diaspora-related services:

- Sending money to recipients back home
- Hiring local services (cleaners, lawyers, errand runners, etc.)
- Verifying documents (land titles, IDs, certificates)
- Airport transfer requests
- Task status tracking

Each request is processed into a structured workflow with AI assistance.

---

## Tech Stack

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, Vanilla JavaScript (no frameworks)
- **Database**: SQLite (`db.sqlite3`)
- **AI Layer**: OpenAI-compatible Chat Completions API (optional, fallback enabled)

---

## System Architecture

```
User Input (Natural Language)
        ↓
AI Intent Extraction (LLM or fallback logic)
        ↓
Entity Parsing & Validation
        ↓
Risk Scoring Engine (0–100)
        ↓
Task Creation (Database Persistence)
        ↓
Workflow Step Generation
        ↓
Multi-Channel Message Generation
(WhatsApp / Email / SMS)
        ↓
Employee Assignment (Finance / Legal / Operations)
        ↓
Task Dashboard (UI)
```

---

## Setup Instructions (Windows / PowerShell)

### 1. Create virtual environment (optional)

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run migrations

```bash
python manage.py migrate
```

### 4. Start server

```bash
python manage.py runserver
```

Open: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## AI Configuration (Optional)

If no API key is provided, the system runs using deterministic fallback logic.

**Environment Variables:**

| Variable | Description |
|---|---|
| `AI_API_KEY` or `OPENAI_API_KEY` | API key |
| `AI_BASE_URL` | Default: `https://api.openai.com/v1` |
| `AI_MODEL` | Default: `gpt-4o-mini` |

---

## Risk Scoring Logic (0–100)

Risk scoring is deterministic and stored per task for auditability.

### Key Factors

**Urgency**
- `urgent` / `asap` / `immediately` → +20

**Customer History**
- Completion ratio > 0.7 → -15
- Completion ratio < 0.3 → +10

**Send Money**
- ≥ 100,000 KES → +30
- ≥ 50,000 KES → +20
- ≥ 20,000 KES → +10
- Missing amount → +10
- Missing recipient → +15
- Missing details → +10 to +20

**Document Verification**
- Land title / title deed → +40
- Other documents → +25
- Missing reference → +10

**Hire Service**
- Missing schedule → +20
- Missing service type/location → +10 each

**Check Status**
- Base → +5
- Missing task code → +20

---

## Database Persistence

All system outputs are stored in SQLite:

- Tasks
- Extracted entities
- Risk scores
- Workflow steps
- Generated messages (WhatsApp, Email, SMS)
- Employee assignments
- Status updates

### SQL Dump Generation

**1. Seed sample tasks**

```bash
python manage.py seed_sample_tasks --min 5
```

**2. Export SQL dump**

```bash
python manage.py export_sql_dump --output sql_dump.sql
```

This generates `sql_dump.sql` with full schema + sample data.

---

## Key Design Decisions

### AI Tools Used

LLM assistance was used for:

- Designing structured JSON output formats
- Validating intent/entity extraction patterns
- Generating example responses for messaging formats

Fallback logic ensures the system works even without external API access.

### System Prompt Design

- Strict JSON-only output enforcement
- Fixed intent taxonomy:
  - `send_money`
  - `hire_service`
  - `verify_document`
  - `airport_transfer`
  - `check_status`
- Structured entity extraction for reliable parsing
- Designed for deterministic backend processing

### Server-Side Control Decisions

Instead of fully trusting LLM output:

- Added server-side validation and normalization
- Enforced SMS length constraints
- Sanitized monetary values
- Ensured safe fallback logic for missing fields

This improves reliability during evaluation.

### Failure Handling

Some LLM providers return malformed JSON or wrapped outputs.

**Solution:**
- Extract first valid JSON block
- Retry once with stricter prompt rules
- Fallback to deterministic parser if needed

---

## What I Learned

- Designing structured AI workflows is more important than raw prompting
- Deterministic fallback systems improve reliability in production-like systems
- Risk scoring must be explainable and auditable, not black-box ML
- Real-world systems require hybrid AI + rules-based architecture

---

## Notes

- No external deployment required for evaluation
- Fully runnable locally
- Designed to work with or without API key
- Built for clarity, explainability, and auditability