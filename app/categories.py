from flask import Blueprint, render_template
from app.db import get_db

bp = Blueprint("categories", __name__, url_prefix="/categories")

@bp.route("/<category_name>")
def category_items(category_name):
    db = get_db()
    #fetching the products under each category 
    cursor = db.execute(
        "SELECT ProductID, ProductName, UnitPrice, UnitsInStock, Discontinued "
        "FROM 'Alphabetical list of products' WHERE CategoryName = ?", 
        (category_name,)
    )
    products = cursor.fetchall()
    if not products:
        return "Category not found or no products available", 404
    db.close()
    return render_template("categories.html", category_name=category_name, products=products)
