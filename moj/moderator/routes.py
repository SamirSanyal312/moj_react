from flask import Blueprint, render_template, flash, redirect, url_for, current_app, request
from moj.roles import role_required
from moj.db import get_db
import logging

bp = Blueprint("moderator", __name__, url_prefix="/moderator")

@bp.route("/dashboard")
@role_required("moderator")
def dashboard():
    #return render_template("moderator/dashboard.html")
    return render_template("moderator/dashboard.html", config=current_app.config)

@bp.route('/manage-users')
@role_required("moderator")
def manage_users():
    db = get_db()
    users = db.execute("SELECT id, nickname, role FROM user").fetchall()
    return render_template("moderator/manage_users.html", users=users)

@bp.route("/update-balance/<int:user_id>", methods=["POST"])
@role_required("moderator")
def update_balance(user_id):
    from flask import request
    #db = get_db()
    new_balance = request.form["balance"]
    db = get_db()

    db.execute("UPDATE user SET joke_balance = ? WHERE id = ?", (new_balance, user_id))
    db.commit()
    flash(f"Updated balance for user ID {user_id} to {new_balance}.")
    print(f"Updated balance for user ID {user_id} to {new_balance}.")    
    return redirect(url_for("moderator.manage_users"))

@bp.route("/toggle-logging", methods=["POST"])
@role_required("moderator")
def toggle_logging():
    current = current_app.config["DEBUG_LOGGING"]
    new_status = not current
    current_app.config["DEBUG_LOGGING"] = new_status

    # Update log handler levels dynamically
    level = logging.DEBUG if new_status else logging.WARNING

    logger = logging.getLogger()
    logger.setLevel(level)
    
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.StreamHandler):  # Only change console handler
            handler.setLevel(level)

    status = "enabled" if new_status else "disabled"
    flash(f"Debug logging {status}.")
    return redirect(url_for("moderator.dashboard"))