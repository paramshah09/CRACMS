# CRACMS — Complete Testing Guide

This guide walks through setting up CRACMS from a clean checkout and verifying every module actually works. All "Expected Result" numbers below assume you've loaded `database/seed_data.sql` and are testing on **June 18, 2026** — the overdue findings count in particular depends on today's actual date, since it's calculated dynamically rather than read from a stored value.

---

## 1. Create a virtual environment

A virtual environment keeps CRACMS's dependencies separate from anything else installed on your system.

**Windows (Command Prompt):**
```
cd cracms
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```
cd cracms
python3 -m venv venv
source venv/bin/activate
```

**Expected result:** Your terminal prompt now shows `(venv)` at the start of the line, e.g. `(venv) C:\cracms>`. This confirms the virtual environment is active — any package you install next goes into this isolated environment, not your system-wide Python.

---

## 2. Install requirements

```
pip install -r requirements.txt
```

**Expected result:** Output ending in something like:
```
Successfully installed Flask-3.1.3 blinker-... click-... itsdangerous-... Jinja2-... MarkupSafe-... Werkzeug-...
```
Flask is the only package listed in `requirements.txt`; the others are its automatic dependencies. If you instead see `command not found: pip`, try `pip3` or `python -m pip install -r requirements.txt`.

---

## 3. Initialize the database

You don't need to run this as a separate manual step — `init_db(app)` inside `app.py`'s `create_app()` function runs `database/schema.sql` automatically every time the app starts, using `CREATE TABLE IF NOT EXISTS` so it's always safe to re-run.

**Expected result (after step 4, once the app has started at least once):** A new file appears at `database/grc.db`. No tables exist with data in them yet at this point — just the empty structure.

**To load the realistic seed data** (25 risks, 5 categories, 3 frameworks, 20 controls, 15 status records, 10 findings) so you have something to actually test against:

**Windows:**
```
sqlite3 database\grc.db < database\seed_data.sql
```

**macOS / Linux:**
```
sqlite3 database/grc.db < database/seed_data.sql
```

If `sqlite3` isn't recognized as a command, you likely don't have the SQLite command-line tool installed separately from Python's built-in `sqlite3` module — install it (e.g. via your package manager) or load the seed file using a short Python one-liner instead:
```
python -c "import sqlite3; sqlite3.connect('database/grc.db').executescript(open('database/seed_data.sql').read())"
```

**Expected result:** No output on success. Verify it worked by running:
```
sqlite3 database/grc.db "SELECT COUNT(*) FROM risks;"
```
which should print `25`.

---

## 4. Run Flask

```
python app.py
```

**Expected result:** Terminal output similar to:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
```
If you see an `ImportError` instead, double-check every file in `routes/` and `utils/` actually exists — `app.py` imports from all of them, and a missing file will fail immediately on startup. Leave this terminal window running and open `http://127.0.0.1:5000` in a browser for the remaining steps.

---

## 5. Verify the Dashboard

Navigate to `http://127.0.0.1:5000/` (the Dashboard is the home page).

**Check** | **Expected result**
---|---
Total Risks KPI | **25**
Open Risks KPI | **17**
Closed Risks KPI | **1**
Total Controls KPI | **20**
Compliant Controls KPI | **3**
Total Findings KPI | **10**
Overdue Findings KPI | **2** (AF-004 and AF-008 — both have due dates before today)
Risk Levels section | Bars for Critical (1), High (12), Medium (10), Low (2), each sized roughly proportional to its share of 25
Compliance Statistics section | Bars for Compliant (3), Partially Compliant (5), Non-Compliant (6) — note these only add up to 14 of the 20 controls, since 1 is "Not Applicable" and 5 have no status record yet
Audit Statistics section | Bars for Open (5), Closed (1), Overdue (2)

If every KPI shows `0` or `—`, the seed data likely wasn't loaded — revisit step 3.

---

## 6. Verify the Risk Register module

Navigate to **Risk Register** in the sidebar.

| Check | How | Expected result |
|---|---|---|
| List loads | Page loads with no action | Table shows 25 rows, sorted by risk score descending — `RSK-001` (score 20, Critical) should be at or near the top |
| Filter by status | Set the Status filter to "Open" | Table narrows to 17 rows |
| Filter by level | Set the Risk Level filter to "Critical" | Table narrows to exactly 1 row: RSK-001 |
| Clear filters | Click "Clear filters" | Table returns to all 25 rows |
| Score preview | Click "+ Add Risk", set Likelihood to 4 and Impact to 5 | The score preview updates live to **20** with a **Critical** badge |
| Create | Fill in Title (required) and Save | A new row appears with an auto-generated code `RSK-026`, and a toast confirms "Risk added to register" |
| Edit | Click "Edit" on any row, change the Owner field, Save | The row updates in place, a confirmation toast appears, and the modal closes |
| Delete | Click "Delete" on the row you just created, confirm | The row disappears from the table after a confirm dialog |

---

## 7. Verify the Compliance module

Navigate to **Compliance** in the sidebar.

| Check | How | Expected result |
|---|---|---|
| Frameworks load | Open the framework dropdown | Three options: ISO/IEC 27001, NIST Cybersecurity Framework, Digital Personal Data Protection Act |
| Controls load | Select "ISO/IEC 27001" | Controls table shows 9 rows (A.5.1 through A.8.28) |
| Status badges | Look at the Status column | A.5.1 shows **Compliant**, A.8.2 shows **Partially Compliant**, A.8.9/A.8.24/A.8.28 show **Non-Compliant**, while A.5.30, A.6.3, A.5.7, and A.8.16 each show a mix — A.6.3 specifically should show **Not Assessed**, since it was deliberately left unassessed in the seed data |
| Switch framework | Select "NIST Cybersecurity Framework" | Controls table updates to show 7 rows instead of 9 |
| Set status | Click "Set Status" on an unassessed control (e.g. ID.AM-01 — wait, this one is already assessed; try PR.PS-01) | A modal opens in create mode (no Delete button), defaulting the assessment date to today |
| Update status | Click "Update" on an already-assessed control | A modal opens pre-filled with its existing status, evidence, and dates, and a Delete button is now visible |
| Add framework | Click "+ Add Framework", enter a name, Save | The new framework appears in the dropdown and is auto-selected |
| Add control | With a framework selected, click "+ Add Control" | The new control appears in the table immediately after saving |

---

## 8. Verify the Audit Findings module

Navigate to **Audit Findings** in the sidebar.

| Check | How | Expected result |
|---|---|---|
| List loads | Page loads with no action | Table shows 10 rows |
| Overdue highlighting | Look at AF-004 and AF-008 | Both show a red **Overdue** badge next to their status badge, and their due dates render in bold red text |
| Filter by severity | Set Severity filter to "Critical" | Table narrows to 2 rows: AF-001 and AF-007 |
| Filter by status | Set Status filter to "Closed" | Table narrows to 1 row: AF-006 |
| Create | Click "+ Add Finding", fill in Title (required), Save | A new row appears with an auto-generated code `AF-011` |
| Edit | Click "Edit" on any row | Modal opens pre-filled with that finding's title, severity, owner, remediation plan, due date, and linked risk (if any) |
| Linked risk dropdown | Open the "Linked Risk" dropdown while adding/editing | Populated with all 25+ risks, shown as `RSK-00X — Title` |
| Delete | Click "Delete", confirm | Row disappears after the confirm dialog |

---

## 9. Verify API endpoints directly

Test the backend independently of the UI using `curl` (or open GET URLs directly in a browser). Run these from a separate terminal while `python app.py` is still running.

| Endpoint | Command | Expected result |
|---|---|---|
| `GET /api/risks/` | `curl http://127.0.0.1:5000/api/risks/` | JSON array of 25 risk objects |
| `GET /api/risks/1` | `curl http://127.0.0.1:5000/api/risks/1` | JSON object for RSK-001, `"risk_score": 20`, `"risk_level": "Critical"` |
| `GET /api/risks/9999` | `curl http://127.0.0.1:5000/api/risks/9999` | `404` status, body: `{"error": "Risk with id 9999 not found"}` |
| `GET /api/risks/categories` | `curl http://127.0.0.1:5000/api/risks/categories` | JSON array of 5 categories |
| `POST /api/risks/` with missing title | `curl -X POST http://127.0.0.1:5000/api/risks/ -H "Content-Type: application/json" -d "{\"likelihood\":3,\"impact\":3}"` | `400` status, body: `{"error": "title is required"}` |
| `GET /api/compliance/frameworks` | `curl http://127.0.0.1:5000/api/compliance/frameworks` | JSON array of 3 frameworks |
| `GET /api/compliance/controls?framework_id=1` | `curl http://127.0.0.1:5000/api/compliance/controls?framework_id=1` | JSON array of 9 controls |
| `GET /api/compliance/status` | `curl http://127.0.0.1:5000/api/compliance/status` | JSON array of 15 status records, each including `control_id`, `control_ref`, and `framework_name` |
| `GET /api/audit-findings/?severity=Critical` | `curl "http://127.0.0.1:5000/api/audit-findings/?severity=Critical"` | JSON array of 2 findings (AF-001, AF-007) |
| `DELETE /api/audit-findings/9999` | `curl -X DELETE http://127.0.0.1:5000/api/audit-findings/9999` | `404` status, body: `{"error": "Audit finding with id 9999 not found"}` |
| `GET /api/dashboard/stats` | `curl http://127.0.0.1:5000/api/dashboard/stats` | Single JSON object with `total_risks: 25`, `compliance_stats.total_controls: 20`, `audit_stats.total_findings: 10`, and so on |

**General pass/fail signal:** every successful request should return JSON (never an HTML error page), every "not found" request should return `404` with a JSON `error` message, and every validation failure should return `400` with a JSON `error` message — never a raw Python traceback. If you see a traceback in the browser or terminal, that's a bug to track down before considering the corresponding module verified.
