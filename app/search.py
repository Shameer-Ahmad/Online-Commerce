from flask import Blueprint, request, render_template
from app.db import get_db

bp = Blueprint("search", __name__, url_prefix="/search")

@bp.route("/")
@bp.route("/results")
def search_results():
    query = request.args.get("q", "").strip()
    db = get_db()
    results = []
    if query:
        cursor = db.execute(
            "SELECT ProductID, ProductName, UnitPrice, CategoryName FROM 'Alphabetical list of products' "
            "WHERE ProductName LIKE ? OR CategoryName LIKE ?",
            (f"%{query}%", f"%{query}%")
        )
        results = cursor.fetchall()
    return render_template("search.html", query=query, results=results)
