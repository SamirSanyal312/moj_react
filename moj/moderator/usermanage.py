from flask import Blueprint, render_template, request, redirect, url_for, flash, g
import logging
from flask import session
from moj.db import get_db
from moj.roles import role_required

bp = Blueprint("usermanage", __name__, url_prefix="/moderator")


@bp.route("/manage-users", methods=["GET", "POST"])
@role_required("moderator")
def manage_users():
    db = get_db()

    if request.method == "POST":
        user_id = request.form["user_id"]
        action = request.form["action"]

        if action == "promote":
            db.execute(
                "UPDATE user SET role = 'moderator' WHERE id = ?", (user_id,))
            db.commit()
            flash("User promoted to moderator.")
            logging.warning(
                f"Role change: user_id={user_id} promoted to moderator, session_id={session.get('sid', 'no-session')}"
            )
        elif action == "demote":
            # Count current moderators
            mods = db.execute(
                "SELECT COUNT(*) as count FROM user WHERE role = 'moderator'").fetchone()["count"]
            if mods <= 1:
                flash("Cannot remove the last moderator.")
                logging.warning(
                    f"Role change refused: attempted to demote last moderator user_id={user_id}, session_id={session.get('sid', 'no-session')}"
                )
            else:
                db.execute(
                    "UPDATE user SET role = 'user' WHERE id = ?", (user_id,))
                db.commit()
                flash("Moderator demoted to user.")
                logging.warning(
                    f"Role change: user_id={user_id} demoted to user, session_id={session.get('sid', 'no-session')}"
                )
        return redirect(url_for("usermanage.manage_users"))

    users = db.execute(
        "SELECT id, nickname, role FROM user ORDER BY id").fetchall()
    return render_template("moderator/manage_users.html", users=users)
