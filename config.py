"""
Configuration settings for CRACMS.

Keeping settings in their own file (instead of scattering them through
app.py) makes it easy to change things like the database location or
debug mode in one place, without touching any application logic.
"""

from pathlib import Path


class Config:
    """
    Central configuration class.
    Loaded into the Flask app via app.config.from_object(Config) in app.py.
    """

    # BASE_DIR is the folder this file (config.py) lives in -- which is
    # the project's root folder. Using __file__ as the anchor (instead of
    # a hardcoded path) means every path below still works correctly no
    # matter which machine or folder the project is run from.
    BASE_DIR = Path(__file__).resolve().parent

    # Full path to the SQLite database file: <project root>/database/grc.db
    # Built with pathlib's "/" operator instead of string concatenation,
    # so it produces correct path separators on Windows, macOS, and Linux.
    DATABASE_PATH = BASE_DIR / "database" / "grc.db"

    # Full path to schema.sql, which contains the CREATE TABLE statements
    # used to set up the database the first time the app runs.
    SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"

    # SECRET_KEY is used internally by Flask to sign session cookies and
    # other security-sensitive data. A fixed value is fine for a local
    # college/learning project like this one; a real production app would
    # load this from an environment variable instead of hardcoding it.
    SECRET_KEY = "cracms-dev-secret-key"

    # DEBUG=True enables Flask's auto-reload (the server restarts itself
    # when you save a file) and detailed in-browser error pages. This
    # should be set to False if the app is ever deployed somewhere other
    # than your own development machine.
    DEBUG = True
