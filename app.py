"""
Cyber Risk Assessment and Compliance Management System (CRACMS)
Application entry point.

This uses Flask's "application factory" pattern: instead of creating
the Flask app as a plain global variable, its creation is wrapped in
a function (create_app). This avoids circular imports between the
blueprints and the app object, and makes the app easier to test later.

NOTE: This file imports from config.py and several routes/ and utils/
modules that do not exist yet (config.py, utils/db.py, routes/risk_routes.py,
routes/compliance_routes.py, routes/audit_routes.py, routes/dashboard_routes.py).
The app will not run until those are created -- this file just defines
the wiring that expects them.
"""

from flask import Flask

# Config and database helpers (utils/db.py, config.py -- not yet created)
from config import Config
from utils.db import init_db, close_db

# Page routes (already built -- serves the 4 HTML pages)
from routes.page_routes import page_bp

# API routes (not yet created -- one blueprint per GRC module)
from routes.risk_routes import risk_bp
from routes.compliance_routes import compliance_bp
from routes.audit_routes import audit_bp
from routes.dashboard_routes import dashboard_bp


def create_app():
    """
    Builds and configures the Flask application.
    Everything the app needs -- settings, database, routes -- is
    assembled here and returned as a ready-to-run app object.
    """
    app = Flask(__name__)

    # Load settings (database path, secret key, etc.) from config.py
    app.config.from_object(Config)

    # Create the database file and all tables if they don't exist yet.
    # Safe to call on every startup, since schema.sql uses
    # "CREATE TABLE IF NOT EXISTS" for every table.
    init_db(app)

    # Register each module's blueprint under its own URL prefix.
    app.register_blueprint(page_bp)                                      # HTML pages: /, /risk-register, /compliance, /audit-findings
    app.register_blueprint(risk_bp, url_prefix="/api/risks")              # Risk Register API
    app.register_blueprint(compliance_bp, url_prefix="/api/compliance")   # Compliance API
    app.register_blueprint(audit_bp, url_prefix="/api/audit-findings")    # Audit Findings API
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")     # Dashboard stats API

    # Make sure the database connection is closed at the end of every
    # request, even if that request raised an error.
    app.teardown_appcontext(close_db)

    return app


# This only runs when the file is executed directly with "python app.py".
# It will NOT run if app.py is imported elsewhere (e.g. by a test file),
# which is the standard, expected Flask behavior.
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
