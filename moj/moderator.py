from flask import Blueprint, render_template
from moj.roles import role_required

bp = Blueprint("moderator", __name__, url_prefix="/moderator")

@bp.route("/dashboard")
@role_required("moderator")
def dashboard():
    return render_template("moderator/dashboard.html")
