"""
Risk Register routes.

Provides full CRUD (Create, Read, Update, Delete) for the risks
table, plus a lookup endpoint for risk categories used to populate
dropdowns on the frontend. risk_score, risk_level, and risk_code are
always calculated/generated here on the backend -- never trusted
from the client -- so this file is the single source of truth for
what a risk's score and code actually are.
"""

import sqlite3
from flask import Blueprint, request, jsonify
from utils.db import get_db
from utils.risk_calculator import evaluate_risk
from utils.helpers import generate_code

risk_bp = Blueprint("risk_bp", __name__)


@risk_bp.route("/categories", methods=["GET"])
def get_risk_categories():
    """Returns every risk category, used to populate dropdowns on the frontend."""
    db = get_db()
    rows = db.execute(
        "SELECT id, name, description FROM risk_categories ORDER BY name"
    ).fetchall()

    # Each row is a sqlite3.Row -- dict(row) converts it into a plain
    # dictionary so jsonify() can turn it into real JSON.
    return jsonify([dict(row) for row in rows]), 200


@risk_bp.route("/", methods=["GET"])
def get_risks():
    """
    Returns all risks, optionally filtered by status, risk_level, or
    category_id via query parameters, e.g.:
        GET /api/risks/?status=Open&risk_level=High
    """
    db = get_db()

    # "WHERE 1=1" is a harmless always-true starting condition that
    # lets every active filter below just be appended with "AND ...".
    query = "SELECT * FROM risks WHERE 1=1"
    params = []

    status = request.args.get("status")
    if status:
        query += " AND status = ?"
        params.append(status)

    risk_level = request.args.get("risk_level")
    if risk_level:
        query += " AND risk_level = ?"
        params.append(risk_level)

    category_id = request.args.get("category_id")
    if category_id:
        query += " AND category_id = ?"
        params.append(category_id)

    query += " ORDER BY risk_score DESC"

    rows = db.execute(query, params).fetchall()
    return jsonify([dict(row) for row in rows]), 200


@risk_bp.route("/<int:risk_id>", methods=["GET"])
def get_risk(risk_id):
    """Returns a single risk by its database id, or a 404 if it doesn't exist."""
    db = get_db()
    row = db.execute("SELECT * FROM risks WHERE id = ?", (risk_id,)).fetchone()

    if row is None:
        return jsonify({"error": f"Risk with id {risk_id} not found"}), 404

    return jsonify(dict(row)), 200


@risk_bp.route("/", methods=["POST"])
def create_risk():
    """
    Creates a new risk.

    Required fields: title, likelihood (1-5), impact (1-5).
    risk_score, risk_level, and risk_code are calculated automatically
    below and are not accepted from the request body.
    """
    data = request.get_json(silent=True) or {}

    title = data.get("title")
    likelihood = data.get("likelihood")
    impact = data.get("impact")

    # --- Validate required fields are present ---
    if not title:
        return jsonify({"error": "title is required"}), 400
    if likelihood is None or impact is None:
        return jsonify({"error": "likelihood and impact are required"}), 400

    # --- Calculate score and level (this also validates the 1-5 range) ---
    try:
        score, level = evaluate_risk(likelihood, impact)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    db = get_db()

    try:
        # Insert with a temporary placeholder for risk_code -- the
        # column is NOT NULL, but we don't know the new row's id
        # (and therefore its real code) until after the insert runs.
        cursor = db.execute("""
            INSERT INTO risks (
                risk_code, title, description, category_id, asset_affected,
                likelihood, impact, risk_score, risk_level, owner,
                status, treatment_plan, identified_date, review_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "PENDING",
            title,
            data.get("description"),
            data.get("category_id"),
            data.get("asset_affected"),
            likelihood,
            impact,
            score,
            level,
            data.get("owner"),
            data.get("status", "Open"),
            data.get("treatment_plan"),
            data.get("identified_date"),
            data.get("review_date")
        ))

        # cursor.lastrowid is the auto-incremented id SQLite just
        # assigned to this row -- exactly what generate_code() needs
        # to build the real "RSK-00X" code.
        new_id = cursor.lastrowid
        risk_code = generate_code("RSK", new_id)

        db.execute("UPDATE risks SET risk_code = ? WHERE id = ?", (risk_code, new_id))
        db.commit()
    except sqlite3.IntegrityError as err:
        # Most likely cause: category_id doesn't match any existing
        # row in risk_categories (a foreign key violation).
        db.rollback()
        return jsonify({"error": f"Could not create risk: {err}"}), 400

    new_row = db.execute("SELECT * FROM risks WHERE id = ?", (new_id,)).fetchone()
    return jsonify(dict(new_row)), 201


@risk_bp.route("/<int:risk_id>", methods=["PUT"])
def update_risk(risk_id):
    """
    Updates an existing risk. Fields left out of the request body keep
    their current value. If likelihood or impact change, risk_score
    and risk_level are recalculated so they never go out of sync.
    """
    db = get_db()
    existing = db.execute("SELECT * FROM risks WHERE id = ?", (risk_id,)).fetchone()

    if existing is None:
        return jsonify({"error": f"Risk with id {risk_id} not found"}), 404

    data = request.get_json(silent=True) or {}

    # Fall back to the current value for anything not sent, so a
    # partial update doesn't accidentally blank out other fields.
    likelihood = data.get("likelihood", existing["likelihood"])
    impact = data.get("impact", existing["impact"])

    try:
        score, level = evaluate_risk(likelihood, impact)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    try:
        db.execute("""
            UPDATE risks SET
                title = ?, description = ?, category_id = ?, asset_affected = ?,
                likelihood = ?, impact = ?, risk_score = ?, risk_level = ?,
                owner = ?, status = ?, treatment_plan = ?, identified_date = ?,
                review_date = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            data.get("title", existing["title"]),
            data.get("description", existing["description"]),
            data.get("category_id", existing["category_id"]),
            data.get("asset_affected", existing["asset_affected"]),
            likelihood,
            impact,
            score,
            level,
            data.get("owner", existing["owner"]),
            data.get("status", existing["status"]),
            data.get("treatment_plan", existing["treatment_plan"]),
            data.get("identified_date", existing["identified_date"]),
            data.get("review_date", existing["review_date"]),
            risk_id
        ))
        db.commit()
    except sqlite3.IntegrityError as err:
        db.rollback()
        return jsonify({"error": f"Could not update risk: {err}"}), 400

    updated_row = db.execute("SELECT * FROM risks WHERE id = ?", (risk_id,)).fetchone()
    return jsonify(dict(updated_row)), 200


@risk_bp.route("/<int:risk_id>", methods=["DELETE"])
def delete_risk(risk_id):
    """Deletes a risk by id."""
    db = get_db()
    existing = db.execute("SELECT id FROM risks WHERE id = ?", (risk_id,)).fetchone()

    if existing is None:
        return jsonify({"error": f"Risk with id {risk_id} not found"}), 404

    db.execute("DELETE FROM risks WHERE id = ?", (risk_id,))
    db.commit()

    return jsonify({"message": f"Risk {risk_id} deleted successfully"}), 200
