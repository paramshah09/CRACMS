"""
Dashboard routes.

Provides a single read-only endpoint that aggregates statistics from
the risks, compliance, and audit_findings tables into one JSON
payload for the dashboard page. Nothing is created or modified here
-- every query is a SELECT/aggregate over data the other route files
already manage.
"""

from datetime import date
from flask import Blueprint, jsonify
from utils.db import get_db

dashboard_bp = Blueprint("dashboard_bp", __name__)


@dashboard_bp.route("/stats", methods=["GET"])
def get_dashboard_stats():
    """
    Returns one JSON object containing risk, compliance, and audit
    statistics, all computed live from the current database state.
    """
    db = get_db()

    # ------------------------------------------------------------
    # Risk counts: total, open, closed
    # ------------------------------------------------------------
    total_risks = db.execute("SELECT COUNT(*) AS count FROM risks").fetchone()["count"]

    open_risks = db.execute(
        "SELECT COUNT(*) AS count FROM risks WHERE status = 'Open'"
    ).fetchone()["count"]

    closed_risks = db.execute(
        "SELECT COUNT(*) AS count FROM risks WHERE status = 'Closed'"
    ).fetchone()["count"]

    # ------------------------------------------------------------
    # Risks grouped by level (Low / Medium / High / Critical)
    # ------------------------------------------------------------
    # Start every level at 0 so the response always has the same
    # shape, even if a level currently has zero risks.
    risks_by_level = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}

    level_rows = db.execute(
        "SELECT risk_level, COUNT(*) AS count FROM risks GROUP BY risk_level"
    ).fetchall()

    for row in level_rows:
        if row["risk_level"] in risks_by_level:
            risks_by_level[row["risk_level"]] = row["count"]

    # ------------------------------------------------------------
    # Compliance statistics
    # ------------------------------------------------------------
    # "Total Controls" counts the controls themselves. The other
    # three counts come from compliance_status, since a control's
    # compliance state is tracked there, not on the control row.
    total_controls = db.execute(
        "SELECT COUNT(*) AS count FROM compliance_controls"
    ).fetchone()["count"]

    compliant_controls = db.execute(
        "SELECT COUNT(*) AS count FROM compliance_status WHERE status = 'Compliant'"
    ).fetchone()["count"]

    non_compliant_controls = db.execute(
        "SELECT COUNT(*) AS count FROM compliance_status WHERE status = 'Non-Compliant'"
    ).fetchone()["count"]

    partially_compliant_controls = db.execute(
        "SELECT COUNT(*) AS count FROM compliance_status WHERE status = 'Partially Compliant'"
    ).fetchone()["count"]

    # ------------------------------------------------------------
    # Audit findings statistics
    # ------------------------------------------------------------
    total_findings = db.execute(
        "SELECT COUNT(*) AS count FROM audit_findings"
    ).fetchone()["count"]

    open_findings = db.execute(
        "SELECT COUNT(*) AS count FROM audit_findings WHERE status = 'Open'"
    ).fetchone()["count"]

    closed_findings = db.execute(
        "SELECT COUNT(*) AS count FROM audit_findings WHERE status = 'Closed'"
    ).fetchone()["count"]

    # "Overdue" is calculated live from due_date rather than trusting
    # a manually-set status -- a finding is overdue if its due_date
    # has already passed and it hasn't been closed yet.
    today = date.today().isoformat()
    overdue_findings = db.execute(
        """
        SELECT COUNT(*) AS count FROM audit_findings
        WHERE status != 'Closed' AND due_date IS NOT NULL AND due_date < ?
        """,
        (today,)
    ).fetchone()["count"]

    # ------------------------------------------------------------
    # Assemble the single response object
    # ------------------------------------------------------------
    return jsonify({
        "total_risks": total_risks,
        "open_risks": open_risks,
        "closed_risks": closed_risks,
        "risks_by_level": risks_by_level,
        "compliance_stats": {
            "total_controls": total_controls,
            "compliant_controls": compliant_controls,
            "non_compliant_controls": non_compliant_controls,
            "partially_compliant_controls": partially_compliant_controls
        },
        "audit_stats": {
            "total_findings": total_findings,
            "open_findings": open_findings,
            "closed_findings": closed_findings,
            "overdue_findings": overdue_findings
        }
    }), 200
