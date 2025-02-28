from flask import Blueprint, render_template
from app.db import get_db

bp = Blueprint('landing', __name__, url_prefix='/')

@bp.route('/')
def landing_page():
    db = get_db()
    cursor = db.execute(
        "SELECT ProductID, ProductName, UnitPrice, UnitsInStock, Discontinued "
        "FROM 'Alphabetical list of products'"
    )
    products = cursor.fetchall()
    db.close()
    return render_template('landing/landing.html',category_name="All Products", products=products )

