# DB setup and helpers
import sqlite3
import click
import logging
from flask import current_app, g
from flask.cli import with_appcontext
# from moj import log_function
from moj.logging_utils import log_function


@log_function
def get_db():
    if 'db' not in g:
        # Establish DB connection
        conn = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Log every SQL statement executed
        conn.set_trace_callback(
            lambda stmt: logging.debug(f"SQL Statement: {stmt}"))
        # Custom row factory to log returned rows

        def log_row_factory(cursor, row):
            record = sqlite3.Row(cursor, row)
            logging.debug(f"SQL returned row: {dict(record)}")
            return record
        conn.row_factory = log_row_factory
        g.db = conn
    return g.db


@log_function
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@log_function
def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
@log_function
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    logging.info(f"Database initialized at {current_app.config['DATABASE']}")
    click.echo('Initialized the database.')


def init_app(app):
    # Check database file availability at startup
    db_path = app.config['DATABASE']
    try:
        conn = sqlite3.connect(db_path)
        conn.close()
    except Exception as e:
        logging.critical(
            f"Database unavailable at startup: cannot open {db_path}",
            exc_info=e
        )
        # Abort startup due to critical error
        raise
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
