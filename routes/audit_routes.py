"""
Audit Findings routes.

Provides full CRUD (Create, Read, Update, Delete) for audit findings.
Each finding can optionally link back to a specific risk via
linked_risk_id, connecting an audit observation to the Risk Register.
finding_code (e.g. AF-001) is always generated here on the backend,
never accepted from the client.
"""

import sqlite3
from flask import Blueprint, request, jsonify
from utils.db import get_db
from utils.helpers import generate_code

audit_bp = Blueprint("audit_bp", __name__)

# Allowed values for severity and status -- kept here as constants so
# both create and update routes validate against the exact same list.
VALID_SEVERITIES = ("Low", "Medium", "High", "Critical")
VALID_STATUSES = ("Open", "In Progress", "Closed", "Overdue")


@audit_bp.route("/", methods=["GET"])
def get_audit_findings():
    """
    Returns all audit findings, optionally filtered by status or
    severity via query parameters, e.g.:
        GET /api/audit-findings/?status=Open&severity=High
    """
    db = get_db()

    # "WHERE 1=1" is a harmless always-true starting condition that
    # lets each active filter below just be appended with "AND ...".
    query = "SELECT * FROM audit_findings WHERE 1=1"
    params = []

    status = request.args.get("status")
    if status:
        query += " AND status = ?"
        params.append(status)

    severity = request.args.get("severity")
    if severity:
        query += " AND severity = ?"
        params.append(severity)

    query += " ORDER BY due_date ASC"

    rows = db.execute(query, params).fetchall()
    return jsonify([dict(row) for row in rows]), 200


@audit_bp.route("/<int:finding_id>", methods=["GET"])
def get_audit_finding(finding_id):
    """Returns a single audit finding by id, or a 404 if it doesn't exist."""
    db = get_db()
    row = db.execute("SELECT * FROM audit_findings WHERE id = ?", (finding_id,)).fetchone()

    if row is None:
        return jsonify({"error": f"Audit finding with id {finding_id} not found"}), 404

    return jsonify(dict(row)), 200


@audit_bp.route("/", methods=["POST"])
def create_audit_finding():
    """
    Creates a new audit finding.

    Required field: title.
    finding_code (e.g. "AF-001") is generated automatically below and
    is not accepted from the request body.
    """
    data = request.get_json(silent=True) or {}
    title = data.get("title")

    if not title:
        return jsonify({"error": "title is required"}), 400

    severity = data.get("severity", "Medium")
    if severity not in VALID_SEVERITIES:
        return jsonify({"error": f"severity must be one of: {', '.join(VALID_SEVERITIES)}"}), 400

    status = data.get("status", "Open")
    if status not in VALID_STATUSES:
        return jsonify({"error": f"status must be one of: {', '.join(VALID_STATUSES)}"}), 400

    db = get_db()

    try:
        # Insert with a temporary placeholder for finding_code -- we
        # don't know the new row's id (and therefore its real code)
        # until after the insert runs.
        cursor = db.execute("""
            INSERT INTO audit_findings (
                finding_code, title, description, severity,
                linked_risk_id, owner, remediation_plan, due_date, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "PENDING",
            title,
            data.get("description"),
            severity,
            data.get("linked_risk_id"),
            data.get("owner"),
            data.get("remediation_plan"),
            data.get("due_date"),
            status
        ))

        # cursor.lastrowid is the auto-incremented id SQLite just
        # assigned -- exactly what generate_code() needs to build the
        # real "AF-00X" code.
        new_id = cursor.lastrowid
        finding_code = generate_code("AF", new_id)

        db.execute("UPDATE audit_findings SET finding_code = ? WHERE id = ?", (finding_code, new_id))
        db.commit()
    except sqlite3.IntegrityError as err:
        # Most likely cause: linked_risk_id doesn't match any existing
        # row in risks (a foreign key violation).
        db.rollback()
        return jsonify({"error": f"Could not create audit finding: {err}"}), 400

    new_row = db.execute("SELECT * FROM audit_findings WHERE id = ?", (new_id,)).fetchone()
    return jsonify(dict(new_row)), 201


@audit_bp.route("/<int:finding_id>", methods=["PUT"])
def update_audit_finding(finding_id):
    """
    Updates an existing audit finding. Fields left out of the request
    body keep their current value.
    """
    db = get_db()
    existing = db.execute("SELECT * FROM audit_findings WHERE id = ?", (finding_id,)).fetchone()

    if existing is None:
        return jsonify({"error": f"Audit finding with id {finding_id} not found"}), 404

    data = request.get_json(silent=True) or {}

    severity = data.get("severity", existing["severity"])
    if severity not in VALID_SEVERITIES:
        return jsonify({"error": f"severity must be one of: {', '.join(VALID_SEVERITIES)}"}), 400

    status = data.get("status", existing["status"])
    if status not in VALID_STATUSES:
        return jsonify({"error": f"status must be one of: {', '.join(VALID_STATUSES)}"}), 400

    try:
        db.execute("""
            UPDATE audit_findings SET
                title = ?, description = ?, severity = ?, linked_risk_id = ?,
                owner = ?, remediation_plan = ?, due_date = ?, status = ?
            WHERE id = ?
        """, (
            data.get("title", existing["title"]),
            data.get("description", existing["description"]),
            severity,
            data.get("linked_risk_id", existing["linked_risk_id"]),
            data.get("owner", existing["owner"]),
            data.get("remediation_plan", existing["remediation_plan"]),
            data.get("due_date", existing["due_date"]),
            status,
            finding_id
        ))
        db.commit()
    except sqlite3.IntegrityError as err:
        db.rollback()
        return jsonify({"error": f"Could not update audit finding: {err}"}), 400

    updated_row = db.execute("SELECT * FROM audit_findings WHERE id = ?", (finding_id,)).fetchone()
    return jsonify(dict(updated_row)), 200


@audit_bp.route("/<int:finding_id>", methods=["DELETE"])
def delete_audit_finding(finding_id):
    """Deletes an audit finding by id."""
    db = get_db()
    existing = db.execute("SELECT id FROM audit_findings WHERE id = ?", (finding_id,)).fetchone()

    if existing is None:
        return jsonify({"error": f"Audit finding with id {finding_id} not found"}), 404

    db.execute("DELETE FROM audit_findings WHERE id = ?", (finding_id,))
    db.commit()

    return jsonify({"message": f"Audit finding {finding_id} deleted successfully"}), 200
