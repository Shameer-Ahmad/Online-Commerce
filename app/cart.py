import secrets
from flask import Blueprint, session, request, g, render_template, redirect, url_for
from datetime import datetime, timedelta
from flask_login import login_required

from app.db import get_db, init_db
# from app.auth import login_required

bp = Blueprint("cart", __name__, url_prefix="/cart")

@bp.route("/")
def view_cart():
    return render_template("cart.html", cart=get_items(), total=calculate_total())

def check_id():
    if "shopper_id" not in session:
        session["shopper_id"] = secrets.token_hex(16)
    return session["shopper_id"]

@bp.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    db = get_db()
    shopper_id = check_id()

    item = db.execute("SELECT quantity FROM Shopping_Cart WHERE product_id = ? AND shopper_id = ?", (product_id, shopper_id)).fetchone()

    if item:
        db.execute("UPDATE Shopping_Cart SET quantity = quantity + 1 WHERE product_id = ? AND shopper_id = ?", (product_id, shopper_id))
    else:
        quantity = int(request.form.get("quantity", 1))
        db.execute('INSERT INTO Shopping_Cart (shopper_id, product_id, quantity) VALUES (?, ?, ?)', (shopper_id, product_id, quantity))

    db.commit()
    return redirect(url_for("cart.view_cart"))
    
def calculate_total():
    items=get_items()
    return sum([item['price'] * item['quantity'] for item in items])

def get_items():
    db = get_db()
    shopper_id = check_id()
    cursor = db.execute("""SELECT Shopping_Cart.id, Shopping_Cart.quantity, Products.ProductName, Products.UnitPrice 
                        FROM Shopping_Cart 
                        JOIN Products ON Shopping_Cart.product_id = Products.ProductID 
                        WHERE Shopping_Cart.shopper_id = ?
                        """, (shopper_id,))
    items = cursor.fetchall()
    return [{'id': row[0], 'quantity': row[1], 'name': row[2], 'price': row[3]} for row in items]

@bp.route("/continue_shopping", methods=["POST"])
def continue_shopping():
    return redirect(url_for("landing.landing_page"))

@bp.route("/remove/<int:item_id>", methods=["POST"])
def remove_one(item_id):
    db = get_db()
    shopper_id = check_id()

    item = db.execute("SELECT quantity FROM Shopping_Cart WHERE id = ? AND shopper_id = ?", (item_id, shopper_id)).fetchone()

    if item and item['quantity'] > 1:
        db.execute("UPDATE Shopping_Cart SET quantity = quantity - 1 WHERE id = ? AND shopper_id = ?", (item_id, shopper_id))
    else:
        db.execute("DELETE FROM Shopping_Cart WHERE id = ? AND shopper_id = ?", (item_id, shopper_id))

    db.commit()
    return redirect(url_for("cart.view_cart"))

@bp.route("/add/<int:item_id>", methods=["POST"])
def add_one(item_id):
    db = get_db()
    shopper_id = check_id()

    item = db.execute("SELECT quantity FROM Shopping_Cart WHERE id = ? AND shopper_id = ?", (item_id, shopper_id)).fetchone()

    if item:
        db.execute("UPDATE Shopping_Cart SET quantity = quantity + 1 WHERE id = ? AND shopper_id = ?", (item_id, shopper_id))

    db.commit()
    return redirect(url_for("cart.view_cart"))

@bp.route("/clear", methods=["POST"])
def clear():
    db = get_db()
    shopper_id = check_id()

    db.execute("DELETE FROM Shopping_Cart WHERE shopper_id = ?", (shopper_id,))

    db.commit()
    return redirect(url_for("cart.view_cart"))

@bp.route("/clean")
def clean():
    db = get_db()
    shopper_id = check_id()

    one_month_ago = datetime.now() - timedelta(days=30)

    # Check intentions of this line with assignment
    db.execute("DELETE FROM Shopping_Cart WHERE created_at < ?", (one_month_ago,))
    #db.execute("DELETE FROM cart WHERE shopper_id = ? AND created_at < ?", (shopper_id, one_month_ago))

    db.commit()
    return redirect(url_for("cart.view_cart"))

@bp.route("/checkout", methods=["POST"])
#@login_required
def checkout():
    db = get_db()

    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    shopper_id = check_id()
    items = db.execute("""
        SELECT Shopping_Cart.product_id, Shopping_Cart.quantity, Products.UnitPrice 
        FROM Shopping_Cart 
        JOIN Products ON Shopping_Cart.product_id = Products.ProductID 
        WHERE shopper_id = ?
    """, (shopper_id,)).fetchall()

    cost = calculate_total()
    
    # Grabs the newest id label to make this new order have that id label
    db.execute("INSERT INTO Orders (CustomerID, OrderDate) VALUES (?, CURRENT_TIMESTAMP)", (session['user_id'],))
    order_id = db.execute("SELECT last_insert_rowid() AS id").fetchone()['id']

    # Insert every item from the cart associated with this user into the order_items table
    for item in items:
        db.execute("INSERT INTO order_items (order_id, product_id, quantity, price, shopper_id) VALUES (?, ?, ?, ?, ?)", 
                   (order_id, item['product_id'], item['quantity'], item['UnitPrice'], shopper_id))
    
    
    clear()
    db.commit()

    # Delete anything from the entire cart where the product has been there for over a month
    clean()

    return redirect(url_for('landing.landing_page'))


