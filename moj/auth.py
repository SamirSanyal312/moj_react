# Registration and login routes
import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from moj.db import get_db
from moj import log_function
import logging

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        nickname = request.form['nickname']
        password = request.form['password']
        db = get_db()
        error = None

        if not email:
            error = 'Email is required.'
        elif not nickname:
            error = 'Nickname is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute('SELECT id FROM user WHERE email = ?', (email,)).fetchone():
            error = 'Email is already registered.'
        elif db.execute('SELECT id FROM user WHERE nickname = ?', (nickname,)).fetchone():
            error = 'Nickname is already taken.'

        if error is None:
            db.execute(
                        "INSERT INTO user (email, password, nickname, role) VALUES (?, ?, ?, ?)",
                        (email, generate_password_hash(password), nickname, "user")
                    )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)
        logging.warning(
            f"Input validation error during registration: {error}, session_id={session.get('sid', 'no-session')}"
        )

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        identifier = request.form['identifier']  # email or nickname
        password = request.form['password']
        db = get_db()
        error = 'Incorrect username or password.'

        user = db.execute(
            'SELECT * FROM user WHERE email = ? OR nickname = ?', (
                identifier, identifier)
        ).fetchone()

        if user is None or not check_password_hash(user['password'], password):
            flash(error)
            logging.warning(
                f"Authentication failure for identifier={identifier}, session_id={session.get('sid', 'no-session')}"
            )
        else:
            session.clear()
            session['user_id'] = user['id']
            logging.info(
                f"Authentication success for user_id={user['id']}, session_id={session.get('sid', 'no-session')}")
            return redirect(url_for('jokes.index'))

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    logging.info(f"User logout, session_id={session.get('sid', 'no-session')}")
    return redirect(url_for('auth.login'))


@bp.before_app_request
@log_function
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@log_function
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            logging.warning(
                f"Unauthorized access attempt to {request.endpoint}, session_id={session.get('sid', 'no-session')}"
            )
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view
