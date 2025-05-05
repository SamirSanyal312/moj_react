from functools import wraps
import logging
from flask import g, redirect, url_for, flash, session, request


def role_required(*roles):  # Accepts multiple roles: "user", "moderator", etc.
    def decorator(view):
        @wraps(view)
        def wrapped_view(**kwargs):
            if g.user is None:
                logging.warning(
                    f"Authorization failure: no user logged in, endpoint={request.endpoint}, session_id={session.get('sid', 'no-session')}"
                )
                flash("You must be logged in.")
                return redirect(url_for("auth.login"))

            user_role = g.user["role"]
            if user_role not in roles:
                logging.warning(
                    f"Authorization failure: user_id={g.user['id']}, role={user_role}, attempted_endpoint={request.endpoint}, allowed_roles={roles}, session_id={session.get('sid', 'no-session')}"
                )
                flash("Unauthorized access.")
                return redirect(url_for("jokes.index"))  # Or another safe page

            logging.info(
                f"Authorization success: user_id={g.user['id']}, role={user_role}, endpoint={request.endpoint}, session_id={session.get('sid', 'no-session')}"
            )
            return view(**kwargs)
        return wrapped_view
    return decorator
