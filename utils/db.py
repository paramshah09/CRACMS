"""
Database connection helpers for CRACMS.

Flask apps shouldn't open a brand new database connection by hand in
every single route. Instead, this file gives each request ONE shared
connection (stored on Flask's special `g` object) and makes sure it's
closed properly once the request finishes. init_db() is a separate,
one-time setup step that creates the database file and its tables.
"""

import sqlite3
from flask import g, current_app


def get_db():
    """
    Returns the database connection for the current request.

    The first time this is called during a request, it opens a new
    sqlite3 connection and stores it on `g`. Every later call to
    get_db() within that same request reuses that same connection
    instead of opening a new one.
    """
    if "db" not in g:
        # current_app gives access to the running Flask app's config,
        # so we can read the database path that config.py defined.
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])

        # row_factory makes each row behave like a dictionary, so
        # columns can be accessed by name (row["title"]) instead of
        # by position (row[2]) -- easier to read and less fragile if
        # a column gets added or reordered later.
        g.db.row_factory = sqlite3.Row

        # SQLite has foreign key enforcement OFF by default. This
        # turns it on for this connection, so the FOREIGN KEY rules
        # in schema.sql are actually enforced.
        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db


def close_db(e=None):
    """
    Closes the database connection at the end of the request, if one
    was opened. Registered in app.py via app.teardown_appcontext(close_db),
    so Flask calls this automatically after every request, whether it
    succeeded or raised an error.

    The `e` parameter exists because Flask always passes any exception
    from the request into teardown functions -- this function doesn't
    need to use it, but it still has to accept it.
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """
    Creates the database file and all its tables (if they don't
    already exist) by running schema.sql against it. Called once
    from create_app() in app.py, every time the app starts.

    Wrapped in "with app.app_context()" because get_db() depends on
    current_app and g, and both only work inside an active Flask
    application context. init_db() runs before the app is handling
    real requests, so this line creates that context manually.
    """
    with app.app_context():
        db = get_db()

        # SCHEMA_PATH is a pathlib.Path object from config.py;
        # Python's open() accepts Path objects directly.
        with open(app.config["SCHEMA_PATH"], "r") as f:
            schema_sql = f.read()

        # executescript() can run multiple SQL statements separated
        # by semicolons in one call -- regular execute() only allows
        # a single statement at a time.
        db.executescript(schema_sql)
        db.commit()
