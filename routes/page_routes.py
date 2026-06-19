"""
Page (view) routes.

The API blueprints built earlier (risk_bp, compliance_bp, audit_bp,
dashboard_bp) only serve JSON -- nothing in the app currently returns
an HTML page. This blueprint adds that missing piece: one route per
page, each just rendering its template. All real data loading happens
client-side via fetch() calls to the API, so these routes stay
intentionally thin.
"""

from flask import Blueprint, render_template

page_bp = Blueprint("page_bp", __name__)


@page_bp.route("/")
def dashboard_page():
    """Serves the Dashboard page."""
    return render_template("dashboard.html")


@page_bp.route("/risk-register")
def risk_register_page():
    """Serves the Risk Register page."""
    return render_template("risk_register.html")


@page_bp.route("/compliance")
def compliance_page():
    """Serves the Compliance Tracking page."""
    return render_template("compliance_tracker.html")


@page_bp.route("/audit-findings")
def audit_findings_page():
    """Serves the Audit Findings Tracker page."""
    return render_template("audit_findings.html")
