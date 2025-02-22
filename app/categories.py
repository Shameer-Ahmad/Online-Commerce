from flask import Blueprint, render_template
from app.db import get_db

bp = Blueprint("categories", __name__, url_prefix="/categories")

@bp.route("/<int:category_id>/")
def category_items(category_id, category_name=None):
    """Show products in a selected category using CategoryID, but fetch CategoryName if missing."""

    db = get_db()

    # If category_name is not provided, fetch it from the database
    if category_name is None:
        cursor = db.execute(
            "SELECT CategoryName FROM Categories WHERE CategoryID = ?", (category_id,)
        )
        category = cursor.fetchone()
        if not category:
            return "Category not found", 404
        category_name = category[0]  # Extract name from tuple

    # Get products using CategoryID
    cursor = db.execute(
        "SELECT ProductID, ProductName, UnitPrice, UnitsInStock, Discontinued "
        "FROM 'Alphabetical list of products' WHERE CategoryID = ?", 
        (category_id,)
    )
    products = cursor.fetchall()

    db.close()

    return render_template("categories.html", category_name=category_name, products=products)
