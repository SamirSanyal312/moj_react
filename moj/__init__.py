from moj.logging_utils import log_function
import os
from flask import Flask, redirect, request, session, g as flask_g
from moj import moderator
import click
from flask import current_app
from moj.db import get_db
from werkzeug.security import generate_password_hash
import logging
import uuid
import functools
import atexit
import signal
import sys
from flask import session


def log_function(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logging.debug(
            f"Entering {func.__module__}.{func.__name__} args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        logging.debug(
            f"Exiting {func.__module__}.{func.__name__} return={result}")
        return result
    return wrapper


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.getcwd(), 'templates')  # 👈 force it!
    )
    app.config['DEBUG_LOGGING'] = False
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'moj.sqlite'),
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import jokes
    app.register_blueprint(jokes.bp)

    # from moj.moderator.routes import bp as moderator_bp
    # app.register_blueprint(moderator_bp)

    from moj.moderator.routes import bp as moderator_bp
    app.register_blueprint(moderator_bp, url_prefix="/moderator")

    from moj.moderator import usermanage
    app.register_blueprint(usermanage.bp)

    from moj import status_api
    app.register_blueprint(status_api.bp)

    from flask_cors import CORS
    CORS(app)

    


    @app.route('/hello')
    @log_function
    def hello():
        return 'Hello, Master of Jokes!'

    @app.route('/')
    @log_function
    def root():
        return redirect('/joke')

    @app.cli.command("create-moderator")
    @click.argument("email")
    @click.argument("nickname")
    @click.argument("password")
    def create_moderator(email, nickname, password):
        """Create a moderator user via CLI."""
        db = get_db()
        if db.execute("SELECT id FROM user WHERE email = ?", (email,)).fetchone():
            click.echo("User with this email already exists.")
            return
        db.execute(
            "INSERT INTO user (email, nickname, password, role, joke_balance) VALUES (?, ?, ?, 'moderator', 0)",
            (email, nickname, generate_password_hash(password))
        )
        db.commit()
        click.echo(f"Moderator '{nickname}' created successfully!")
        logging.info(
            f"Moderator created: email={email}, nickname={nickname}, session_id={session.get('sid', 'no-session')}"
        )

    @app.before_request
    @log_function
    def log_session_id():
        # Assign a new session ID if not present
        if 'sid' not in session:
            session['sid'] = uuid.uuid4().hex
            logging.info(f"Assigned new session ID: {session['sid']}")
        # Attach to Flask global and log for debug
        logging.debug(f"Session ID for request: {session['sid']}")

    @app.after_request
    def log_request(response):
        # Log method, path, session ID, endpoint, and status code
        sid = session.get('sid', 'no-session')
        endpoint = request.endpoint or 'unknown'
        message = (
            f"{request.method} {request.path} endpoint={endpoint} "
            f"session_id={sid} status={response.status_code}"
        )
        if response.status_code != 200:
            logging.warning(message)
        else:
            logging.info(message)
        return response

    @app.teardown_request
    def log_unhandled_exception(error):
        if error is not None:
            sid = session.get('sid', 'no-session')
            endpoint = request.endpoint or 'unknown'
            logging.error(
                f"Unhandled exception in {request.method} {request.path} endpoint={endpoint} session_id={sid}",
                exc_info=error
            )

    # Set up logging with separate console and file handlers
    # Remove existing handlers to prevent duplicate logs
    logging.getLogger().handlers.clear()

    # Set up logging based on DEBUG_LOGGING config
    logger = logging.getLogger()
    logger.setLevel(
        logging.DEBUG if app.config['DEBUG'] else logging.INFO)

    formatter = logging.Formatter(
        fmt='%(asctime)s %(levelname)s [%(module)s] %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S'
    )

    # File handler (always log INFO and above to file)
    file_handler = logging.FileHandler('moj.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler (controlled by DEBUG flag)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(
        logging.DEBUG if app.config['DEBUG'] else logging.WARN)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Suppress werkzeug default logs unless debugging
    logging.getLogger('werkzeug').setLevel(logging.WARNING)

    # Log startup configuration
    logging.info(
        f"App starting with SECRET_KEY={app.config['SECRET_KEY']!r}, "
        f"DATABASE={app.config['DATABASE']}, DEBUG={app.debug}"
    )

    # Register application shutdown log
    def log_app_shutdown():
        logging.info("Master of Jokes shutting down")
    atexit.register(log_app_shutdown)

    # Handle abnormal exit signals
    def handle_exit_signal(signum, frame):
        sid = session.get('sid', 'no-session')
        logging.critical(
            f"Abnormal exit signal {signum} received, session_id={sid}")
        sys.exit(1)

    signal.signal(signal.SIGINT, handle_exit_signal)
    signal.signal(signal.SIGTERM, handle_exit_signal)

    logging.info("Initialized Master of Jokes - Version 2.0")

    @app.context_processor
    def inject_debug_flag():
        return {'config': app.config}

    return app
