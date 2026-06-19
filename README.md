# Cyber Risk Assessment & Compliance Management System (CRACMS)

A full-stack GRC (Governance, Risk, and Compliance) web application built as an academic project to demonstrate practical information security management concepts. CRACMS implements real-world workflows used by GRC analysts, internal auditors, and compliance officers — including a 5×5 risk scoring matrix, multi-framework compliance tracking, and an audit findings lifecycle — in a clean, self-contained local deployment.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Architecture](#architecture)
- [Database Design](#database-design)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Screenshots](#screenshots)
- [Future Enhancements](#future-enhancements)
- [Learning Outcomes](#learning-outcomes)

---

## Project Overview

CRACMS was designed to bridge the gap between theoretical GRC concepts taught in a Cyber Security curriculum and the practical tooling that organisations actually use. Rather than using a generic CRUD app as a portfolio project, this system models the three pillars of an information security management program:

- **Risk management** — identify, score, and track risks using a Likelihood × Impact matrix aligned with ISO 31000 principles.
- **Compliance tracking** — map controls to frameworks such as ISO/IEC 27001:2022, NIST CSF 2.0, or the Digital Personal Data Protection Act (DPDP) 2023, and record assessment status per control.
- **Audit management** — log findings from internal or external audits, assign owners and remediation plans, and track each finding through to closure.

The system is intentionally built without heavy frameworks or ORMs, so every layer — SQL schema, HTTP routing, frontend DOM manipulation — is visible and readable. This makes it a practical learning artefact as well as a deployable tool.

---

## Features

### Risk Register
- Create and manage risks with auto-generated sequential codes (`RSK-001`, `RSK-002`, …)
- Automatic risk score calculation: **Score = Likelihood × Impact** (1–5 scale each)
- Automatic risk level classification: Low (1–4) · Medium (5–9) · High (10–16) · Critical (17–25)
- Live score preview in the add/edit modal — updates instantly as likelihood and impact are changed
- Filter risks by status, risk level, or category
- Full CRUD: create, read, update, delete

### Compliance Tracker
- Define unlimited compliance frameworks with version and description metadata
- Add individual controls under each framework (reference, name, domain, description)
- Record and update compliance status per control: Compliant · Partially Compliant · Non-Compliant · Not Applicable
- Link compliance status records to specific risks in the Risk Register
- Track evidence, responsible person, last assessed date, and next review date per control

### Audit Findings Tracker
- Log findings from internal or external audits with auto-generated codes (`AF-001`, `AF-002`, …)
- Severity classification: Low · Medium · High · Critical
- Status lifecycle: Open → In Progress → Closed / Overdue
- Dynamic overdue detection: a finding is highlighted as overdue client-side if its due date has passed and it has not been closed — without requiring a manual status update
- Link findings to risks in the Risk Register

### Dashboard
- Summary KPIs: total risks, open risks, closed risks, total controls, compliant controls, total findings, overdue findings
- Risk Levels breakdown: proportional bar chart across Critical / High / Medium / Low
- Compliance Statistics: Compliant / Partially Compliant / Non-Compliant as a share of total controls
- Audit Statistics: Open / Closed / Overdue findings at a glance
- All dashboard data loaded via a single aggregated API call — no separate round-trips

### Security practices built into the codebase
- All user-supplied text passed through `escapeHtml()` before DOM insertion — guards against stored XSS
- Parameterised SQL queries throughout — no string concatenation in SQL
- SQLite foreign key enforcement enabled per connection
- Input validation on both client (score preview) and server (required fields, range checks, allowed enum values) — the backend is always the authoritative source of truth

---

## Architecture

CRACMS follows a three-tier architecture:

```
┌─────────────────────────────────────────┐
│           Browser (Frontend)            │
│  HTML templates · CSS · Vanilla JS      │
│  Fetch API → JSON · No JS framework     │
└───────────────┬─────────────────────────┘
                │ HTTP / JSON
┌───────────────▼─────────────────────────┐
│          Flask Application              │
│  App factory · Blueprint routing        │
│  Risk · Compliance · Audit · Dashboard  │
│  utils: db · risk_calculator · helpers  │
└───────────────┬─────────────────────────┘
                │ sqlite3
┌───────────────▼─────────────────────────┐
│          SQLite Database                │
│  schema.sql (7 tables)                  │
│  grc.db (auto-created on first run)     │
└─────────────────────────────────────────┘
```

**Flask Blueprints** are used to group related routes, keeping each GRC module self-contained:

| Blueprint | URL prefix | Responsibility |
|---|---|---|
| `page_bp` | `/` | Serves the four HTML pages |
| `risk_bp` | `/api/risks` | Risk Register CRUD + category lookup |
| `compliance_bp` | `/api/compliance` | Frameworks, controls, and status CRUD |
| `audit_bp` | `/api/audit-findings` | Audit Findings CRUD |
| `dashboard_bp` | `/api/dashboard` | Aggregated read-only stats endpoint |

The frontend makes no assumptions about IDs or state between page loads — every page fetches its own data on `DOMContentLoaded` and the shared `common.js` module provides all cross-page helpers (fetch wrapper, toasts, escaping, badge generators, modal controls).

---

## Database Design

```
risk_categories ◄─────────────────────────── risks
     id                                          id (PK)
     name                                        risk_code (UNIQUE)
     description                                 title
                                                 category_id (FK → risk_categories)
                                                 likelihood, impact
                                                 risk_score, risk_level
                                                 owner, status, treatment_plan
                                                 identified_date, review_date

compliance_frameworks ◄── compliance_controls ◄── compliance_status
     id                        id (PK)                 id (PK)
     name                      framework_id (FK)        control_id (FK → compliance_controls)
     version                   control_ref              status
     description               control_name             evidence, responsible_person
                               domain                   linked_risk_id (FK → risks)
                               control_description      last_assessed_date, next_review_date

audit_findings
     id (PK)
     finding_code (UNIQUE)
     title, description, severity
     linked_risk_id (FK → risks)
     owner, remediation_plan, due_date
     status
```

**Design decisions:**
- `risk_score` and `risk_level` are stored (not computed on read) so they can be filtered, sorted, and aggregated by SQL without re-deriving them on every query.
- `compliance_status` is a separate table from `compliance_controls` — a control's definition and an organisation's current state against it change independently. This allows repeated re-assessments without mutating the control record.
- All `CREATE TABLE` statements use `IF NOT EXISTS` so the schema initialisation script is safe to run on every application startup without risk of data loss.
- Foreign key enforcement is activated per connection via `PRAGMA foreign_keys = ON` in `utils/db.py`.

---

## Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| Language | Python 3.11+ | Type-safe pathlib, f-string formatting throughout |
| Web framework | Flask 3.1.3 | App factory pattern, Blueprint routing |
| Database | SQLite 3 | `sqlite3` stdlib — no ORM, raw SQL with parameterised queries |
| Frontend | HTML5 · CSS3 · Vanilla JavaScript (ES6+) | No React, Vue, or jQuery |
| Fonts | Google Fonts (Space Grotesk · Inter · IBM Plex Mono) | CDN link, no local files |
| Styling | Custom CSS with design tokens (`--var` properties) | No Tailwind or Bootstrap |
| Database tooling | SQLite CLI / Python one-liner | Schema and seed scripts only |
| Dependency management | pip + `requirements.txt` | Single external dependency (Flask) |

All other imports (`sqlite3`, `pathlib`, `datetime`, `json`) are Python standard library — no hidden dependencies.

---

## Installation

### Prerequisites
- Python 3.11 or newer
- pip
- Git

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/<your-username>/cracms.git
cd cracms
```

**2. Create and activate a virtual environment**
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the application**
```bash
python app.py
```
The database file (`database/grc.db`) and all tables are created automatically on first startup.

**5. (Optional) Load seed data**

To populate the application with 25 realistic college IT scenario risks, 3 compliance frameworks, 20 controls, 15 status records, and 10 audit findings:

```bash
# macOS / Linux
sqlite3 database/grc.db < database/seed_data.sql

# Windows
sqlite3 database\grc.db < database\seed_data.sql
```

**6. Open in browser**

Navigate to `http://127.0.0.1:5000`

---

## Usage

| Page | URL | Description |
|---|---|---|
| Dashboard | `http://127.0.0.1:5000/` | KPI summary and breakdown charts |
| Risk Register | `http://127.0.0.1:5000/risk-register` | View, add, edit, filter, and delete risks |
| Compliance | `http://127.0.0.1:5000/compliance` | Manage frameworks, controls, and assessment status |
| Audit Findings | `http://127.0.0.1:5000/audit-findings` | Log and track audit observations through to closure |

All data entry is done through in-page modal dialogs — no separate form pages. Every module supports full create, read, update, and delete without a page reload.

---

## API Endpoints

All API responses are JSON. All write operations (`POST`, `PUT`, `DELETE`) require `Content-Type: application/json`.

### Risk Register

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/risks/` | List all risks (supports `?status=`, `?risk_level=`, `?category_id=` filters) |
| `GET` | `/api/risks/<id>` | Get a single risk |
| `POST` | `/api/risks/` | Create a risk (required: `title`, `likelihood`, `impact`) |
| `PUT` | `/api/risks/<id>` | Update a risk (partial updates supported) |
| `DELETE` | `/api/risks/<id>` | Delete a risk |
| `GET` | `/api/risks/categories` | List all risk categories |

### Compliance

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/compliance/frameworks` | List all compliance frameworks |
| `POST` | `/api/compliance/frameworks` | Create a framework (required: `name`) |
| `GET` | `/api/compliance/controls` | List controls (supports `?framework_id=` filter) |
| `POST` | `/api/compliance/controls` | Create a control (required: `framework_id`, `control_ref`, `control_name`) |
| `GET` | `/api/compliance/status` | List all compliance status records (joined with control and framework names) |
| `POST` | `/api/compliance/status` | Create a status record (required: `control_id`) |
| `PUT` | `/api/compliance/status/<id>` | Update a status record |
| `DELETE` | `/api/compliance/status/<id>` | Delete a status record |

### Audit Findings

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/audit-findings/` | List all findings (supports `?status=`, `?severity=` filters) |
| `GET` | `/api/audit-findings/<id>` | Get a single finding |
| `POST` | `/api/audit-findings/` | Create a finding (required: `title`) |
| `PUT` | `/api/audit-findings/<id>` | Update a finding |
| `DELETE` | `/api/audit-findings/<id>` | Delete a finding |

### Dashboard

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/dashboard/stats` | Aggregated stats: risk counts by level and status, compliance counts, audit counts |

**Sample response — `GET /api/dashboard/stats`:**
```json
{
  "total_risks": 25,
  "open_risks": 17,
  "closed_risks": 1,
  "risks_by_level": { "Low": 2, "Medium": 10, "High": 12, "Critical": 1 },
  "compliance_stats": {
    "total_controls": 20,
    "compliant_controls": 3,
    "non_compliant_controls": 6,
    "partially_compliant_controls": 5
  },
  "audit_stats": {
    "total_findings": 10,
    "open_findings": 5,
    "closed_findings": 1,
    "overdue_findings": 2
  }
}
```

---

## Screenshots

> _Screenshots to be added after the first local deployment._

| Page | Preview |
|---|---|
| Dashboard | _[ dashboard-screenshot.png ]_ |
| Risk Register | _[ risk-register-screenshot.png ]_ |
| Compliance Tracker | _[ compliance-screenshot.png ]_ |
| Audit Findings | _[ audit-findings-screenshot.png ]_ |

---

## Future Enhancements

- **User authentication and role-based access control** — Admin, Risk Manager, Auditor, Viewer roles defined in the `users` table but not yet wired to a login flow
- **Risk treatment workflow** — a dedicated status history log showing how a risk's score and treatment plan changed over time
- **Compliance percentage reporting** — per-framework coverage metrics showing what proportion of controls have been assessed
- **Risk heat map** — an interactive 5×5 Likelihood × Impact grid showing how many risks occupy each cell
- **Email notifications** — alerts when findings approach or pass their due date, or when a risk's review date arrives
- **PDF/CSV export** — one-click report generation for Risk Register and Audit Findings for submission to management
- **REST API key authentication** — simple API key header validation so the JSON endpoints can be called from external tools
- **Multi-user deployment** — PostgreSQL backend and a proper WSGI server (Gunicorn + Nginx) for a shared team environment

---

## Learning Outcomes

Building CRACMS involved applying and connecting concepts across multiple areas of a Cyber Security curriculum:

**Information Security Management**
- Practical implementation of a Likelihood × Impact risk matrix aligned with ISO 31000 risk assessment methodology
- Understanding of the three-table model (frameworks → controls → status) that underpins real ISMS compliance programs like ISO/IEC 27001
- Familiarity with GRC terminology: risk appetite, control domains, audit findings lifecycle, corrective action tracking

**Secure Software Development**
- Parameterised SQL queries as the primary defence against SQL injection — every query in the codebase uses `?` placeholders rather than string formatting
- HTML-escaping of all user-supplied data before DOM insertion (`escapeHtml()`) as a defence against stored Cross-Site Scripting (XSS)
- Input validation at both the client and server layers, with the backend treated as the sole source of truth
- Foreign key enforcement and database constraint checking as data integrity controls

**Web Application Development**
- Flask application factory pattern and Blueprint-based modular routing
- RESTful API design: correct HTTP verbs (GET/POST/PUT/DELETE), appropriate status codes (200/201/400/404), and JSON error envelopes
- Vanilla JavaScript ES6 patterns: `async/await`, `fetch()`, template literals, destructuring, and `URLSearchParams` for filtered API calls
- CSS custom properties (design tokens) for consistent theming across a multi-page application without a component framework

**Database Design**
- Normalised relational schema design with deliberate foreign key relationships
- Trade-off analysis: storing `risk_score` and `risk_level` as computed columns for query performance vs. deriving them on read
- Safe schema initialisation using idempotent `CREATE TABLE IF NOT EXISTS` statements

---

## Project Structure

```
cracms/
├── app.py                    # Flask application factory, blueprint registration
├── config.py                 # Centralised configuration (paths, secret key, debug)
├── requirements.txt          # Single external dependency: Flask 3.1.3
├── database/
│   ├── schema.sql            # All 7 CREATE TABLE IF NOT EXISTS statements
│   ├── seed_data.sql         # Realistic test data (25 risks, 3 frameworks, ...)
│   └── grc.db                # Auto-created SQLite database (not committed to git)
├── routes/
│   ├── page_routes.py        # Serves HTML pages
│   ├── risk_routes.py        # Risk Register API
│   ├── compliance_routes.py  # Compliance API
│   ├── audit_routes.py       # Audit Findings API
│   └── dashboard_routes.py   # Dashboard stats API
├── utils/
│   ├── db.py                 # Per-request SQLite connection via Flask g
│   ├── risk_calculator.py    # Likelihood × Impact scoring logic
│   └── helpers.py            # Sequential code generator (RSK-001, AF-001, ...)
├── templates/
│   ├── dashboard.html
│   ├── risk_register.html
│   ├── compliance_tracker.html
│   └── audit_findings.html
└── static/
    ├── css/
    │   └── style.css         # Full design system (tokens, layout, components)
    └── js/
        ├── common.js         # Shared helpers (fetch, toasts, escaping, badges)
        ├── dashboard.js
        ├── risk.js
        ├── compliance.js
        └── audit.js
```

---

## Author

**Param Shah**
B.Tech Cyber Security · Shah & Anchor Kutchhi Engineering College (SAKEC)

---

## License

This project was developed for academic purposes. Feel free to reference or adapt it for educational use.
