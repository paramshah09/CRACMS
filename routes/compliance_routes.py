"""
Compliance Tracking routes.

Handles three related entities:
  - compliance_frameworks  (e.g. ISO 27001:2022, NIST CSF 2.0)
  - compliance_controls    (individual controls belonging to a framework)
  - compliance_status      (how compliant the organization is against
                             each control, optionally linked to a risk)
"""

import sqlite3
from flask import Blueprint, request, jsonify
from utils.db import get_db

compliance_bp = Blueprint("compliance_bp", __name__)


# ---------------------------------------------------------------
# Frameworks
# ---------------------------------------------------------------

@compliance_bp.route("/frameworks", methods=["GET"])
def get_frameworks():
    """Returns every compliance framework (e.g. ISO 27001:2022, NIST CSF 2.0)."""
    db = get_db()
    rows = db.execute("SELECT * FROM compliance_frameworks ORDER BY name").fetchall()
    return jsonify([dict(row) for row in rows]), 200


@compliance_bp.route("/frameworks", methods=["POST"])
def create_framework():
    """
    Creates a new compliance framework.
    Required field: name (e.g. "ISO 27001:2022").
    """
    data = request.get_json(silent=True) or {}
    name = data.get("name")

    if not name:
        return jsonify({"error": "name is required"}), 400

    db = get_db()
    db.execute(
        "INSERT INTO compliance_frameworks (name, version, description) VALUES (?, ?, ?)",
        (name, data.get("version"), data.get("description"))
    )
    db.commit()

    new_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    new_row = db.execute("SELECT * FROM compliance_frameworks WHERE id = ?", (new_id,)).fetchone()
    return jsonify(dict(new_row)), 201


# ---------------------------------------------------------------
# Controls
# ---------------------------------------------------------------

@compliance_bp.route("/controls", methods=["GET"])
def get_controls():
    """
    Returns all controls across every framework. Can be narrowed to a
    single framework with an optional query parameter, e.g.:
        GET /api/compliance/controls?framework_id=1
    """
    db = get_db()
    framework_id = request.args.get("framework_id")

    if framework_id:
        rows = db.execute(
            "SELECT * FROM compliance_controls WHERE framework_id = ? ORDER BY control_ref",
            (framework_id,)
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT * FROM compliance_controls ORDER BY framework_id, control_ref"
        ).fetchall()

    return jsonify([dict(row) for row in rows]), 200


@compliance_bp.route("/controls", methods=["POST"])
def create_control():
    """
    Creates a new control under a given framework.
    Required fields: framework_id, control_ref, control_name.
    """
    data = request.get_json(silent=True) or {}
    framework_id = data.get("framework_id")
    control_ref = data.get("control_ref")
    control_name = data.get("control_name")

    if not framework_id or not control_ref or not control_name:
        return jsonify({"error": "framework_id, control_ref, and control_name are required"}), 400

    db = get_db()
    try:
        db.execute("""
            INSERT INTO compliance_controls (framework_id, control_ref, control_name, control_description, domain)
            VALUES (?, ?, ?, ?, ?)
        """, (framework_id, control_ref, control_name, data.get("control_description"), data.get("domain")))
        db.commit()
    except sqlite3.IntegrityError as err:
        # Most likely cause: framework_id doesn't match any existing
        # row in compliance_frameworks (a foreign key violation).
        db.rollback()
        return jsonify({"error": f"Could not create control: {err}"}), 400

    new_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    new_row = db.execute("SELECT * FROM compliance_controls WHERE id = ?", (new_id,)).fetchone()
    return jsonify(dict(new_row)), 201


# ---------------------------------------------------------------
# Compliance Status
# ---------------------------------------------------------------

@compliance_bp.route("/status", methods=["GET"])
def get_compliance_status():
    """
    Returns every compliance status record, joined with its control
    and framework names so the frontend doesn't need separate lookups
    just to display something readable.
    """
    db = get_db()
    rows = db.execute("""
        SELECT
            cs.id, cs.control_id, cs.status, cs.evidence, cs.responsible_person,
            cs.linked_risk_id, cs.last_assessed_date, cs.next_review_date, cs.notes,
            cc.control_ref, cc.control_name, cf.name AS framework_name
        FROM compliance_status cs
        JOIN compliance_controls cc ON cs.control_id = cc.id
        JOIN compliance_frameworks cf ON cc.framework_id = cf.id
        ORDER BY cf.name, cc.control_ref
    """).fetchall()
    return jsonify([dict(row) for row in rows]), 200


@compliance_bp.route("/status", methods=["POST"])
def create_compliance_status():
    """
    Creates a compliance status record for a control.
    Required field: control_id.
    """
    data = request.get_json(silent=True) or {}
    control_id = data.get("control_id")

    if not control_id:
        return jsonify({"error": "control_id is required"}), 400

    db = get_db()
    try:
        db.execute("""
            INSERT INTO compliance_status (
                control_id, status, evidence, responsible_person,
                linked_risk_id, last_assessed_date, next_review_date, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            control_id,
            data.get("status", "Non-Compliant"),
            data.get("evidence"),
            data.get("responsible_person"),
            data.get("linked_risk_id"),
            data.get("last_assessed_date"),
            data.get("next_review_date"),
            data.get("notes")
        ))
        db.commit()
    except sqlite3.IntegrityError as err:
        # Most likely cause: control_id or linked_risk_id doesn't
        # match an existing row (a foreign key violation).
        db.rollback()
        return jsonify({"error": f"Could not create status record: {err}"}), 400

    new_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    new_row = db.execute("SELECT * FROM compliance_status WHERE id = ?", (new_id,)).fetchone()
    return jsonify(dict(new_row)), 201


@compliance_bp.route("/status/<int:status_id>", methods=["PUT"])
def update_compliance_status(status_id):
    """Updates an existing compliance status record. Fields left out keep their current value."""
    db = get_db()
    existing = db.execute("SELECT * FROM compliance_status WHERE id = ?", (status_id,)).fetchone()

    if existing is None:
        return jsonify({"error": f"Compliance status record with id {status_id} not found"}), 404

    data = request.get_json(silent=True) or {}

    try:
        db.execute("""
            UPDATE compliance_status SET
                status = ?, evidence = ?, responsible_person = ?, linked_risk_id = ?,
                last_assessed_date = ?, next_review_date = ?, notes = ?
            WHERE id = ?
        """, (
            data.get("status", existing["status"]),
            data.get("evidence", existing["evidence"]),
            data.get("responsible_person", existing["responsible_person"]),
            data.get("linked_risk_id", existing["linked_risk_id"]),
            data.get("last_assessed_date", existing["last_assessed_date"]),
            data.get("next_review_date", existing["next_review_date"]),
            data.get("notes", existing["notes"]),
            status_id
        ))
        db.commit()
    except sqlite3.IntegrityError as err:
        db.rollback()
        return jsonify({"error": f"Could not update status record: {err}"}), 400

    updated_row = db.execute("SELECT * FROM compliance_status WHERE id = ?", (status_id,)).fetchone()
    return jsonify(dict(updated_row)), 200


@compliance_bp.route("/status/<int:status_id>", methods=["DELETE"])
def delete_compliance_status(status_id):
    """Deletes a compliance status record by id."""
    db = get_db()
    existing = db.execute("SELECT id FROM compliance_status WHERE id = ?", (status_id,)).fetchone()

    if existing is None:
        return jsonify({"error": f"Compliance status record with id {status_id} not found"}), 404

    db.execute("DELETE FROM compliance_status WHERE id = ?", (status_id,))
    db.commit()

    return jsonify({"message": f"Compliance status {status_id} deleted successfully"}), 200
