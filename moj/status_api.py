from flask import Blueprint, jsonify
from moj.db import get_db

bp = Blueprint("status_api", __name__, url_prefix="/api")

@bp.route("/status", methods=["GET"])
def status_report():
    db = get_db()
    num_users = db.execute("SELECT COUNT(*) FROM user").fetchone()[0]
    num_jokes = db.execute("SELECT COUNT(*) FROM joke").fetchone()[0]
    return jsonify({"users": num_users, "jokes": num_jokes})
