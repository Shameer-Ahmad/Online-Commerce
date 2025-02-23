import secrets
from flask import Blueprint, session, request, g, render_template, redirect, url_for
from datetime import datetime, timedelta

from app.db import get_db, init_db

bp = Blueprint("cart", __name__, url_prefix="/cart")

@bp.route("/")
def view_cart():
    return render_template("cart.html", cart=get_items(), total=calculate_total())

"""   
def get_db():
    import sqlite3
    if 'db' not in g:
        g.db = sqlite3.connect(':memory:')
        g.db.execute('CREATE TABLE cart (id INTEGER PRIMARY KEY, shopper_id TEXT, product_id TEXT, quantity INTEGER)')
        g.db.execute('CREATE TABLE products (id TEXT PRIMARY KEY, name TEXT, price REAL)')
        g.db.execute('INSERT INTO products (id, name, price) VALUES ("1", "Product 1", 10.0)')
        g.db.execute('INSERT INTO products (id, name, price) VALUES ("3", "Product 3", 30.0)')
    return g.db
"""
def check_id():
    if "shopper_id" not in session:
        session["shopper_id"] = secrets.token_hex(16)
    return session["shopper_id"]

def add_to_cart(product_id, quantity):
    db = get_db()
    shopper_id = check_id()
    db.execute("insert into cart (shopper_id, product_id, quantity) values (?,?,?)", 
               (shopper_id, product_id, quantity),)
    db.commit()

def calculate_total():
    items=get_items()
    return sum([item['price'] * item['quantity'] for item in items])

def get_items():
    db = get_db()
    shopper_id = check_id()
    cursor = db.execute("""SELECT cart.id, cart.quantity, Products.ProductName, Products.UnitPrice 
                        FROM cart 
                        JOIN Products ON cart.product_id = Products.ProductID 
                        WHERE cart.shopper_id = ?
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

    item = db.execute("SELECT quantity FROM cart WHERE id = ? AND shopper_id = ?", (item_id, shopper_id)).fetchone()

    if item and item['quantity'] > 1:
        db.execute("UPDATE cart SET quantity = quantity - 1 WHERE id = ? AND shopper_id = ?", (item_id, shopper_id))
    else:
        db.execute("DELETE FROM cart WHERE id = ? AND shopper_id = ?", (item_id, shopper_id))

    db.commit()
    return redirect(url_for("cart.view_cart"))

@bp.route("/add/<int:item_id>", methods=["POST"])
def add_one(item_id):
    db = get_db()
    shopper_id = check_id()

    item = db.execute("SELECT quantity FROM cart WHERE id = ? AND shopper_id = ?", (item_id, shopper_id)).fetchone()

    if item:
        db.execute("UPDATE cart SET quantity = quantity + 1 WHERE id = ? AND shopper_id = ?", (item_id, shopper_id))

    db.commit()
    return redirect(url_for("cart.view_cart"))

@bp.route('/clean')
def clean():
    db = get_db()
    shopper_id = check_id()

    one_month_ago = datetime.now() - timedelta(days=30)

    # Check intentions of this line with assignment
    db.execute("DELETE FROM cart WHERE created_at < ?", (shopper_id, one_month_ago))
    #db.execute("DELETE FROM cart WHERE shopper_id = ? AND created_at < ?", (shopper_id, one_month_ago))

    db.commit()
    return redirect(url_for("cart.view_cart"))

@bp.route('/checkout', methods=['POST'])
def checkout():
    db = get_db()

    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    shopper_id = check_id()
    items = db.execute("SELECT cart.product_id, cart.quantity, products.price FROM cart WHERE shopper_id = ?", (shopper_id,)).fetchall()

    # Get total cost of items
    cost = calculate_total()
    
    # Grabs the newest id label to make this new order have that id label
    db.execute("INSERT INTO Orders (CustomerID, OrderDate) VALUES (?, CURRENT_TIMESTAMP)", (session['user_id'],))
    order_id = db.execute("SELECT last_insert_rowid() AS id").fetchone()['id']

    # Insert every item from the cart associated with this user into the order_items table
    for item in items:
        db.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)", (order_id, item['product_id'], item['quantity'], item['price'] ))
    
    # Delete that user's old items from the cart
    db.execute("DELETE FROM cart WHERE shopper_id = ?", (shopper_id,))
    
    db.commit()

    # Delete anything from the entire cart where the product has been there for over a month
    clean()


@bp.route("/add_test_items")
def add_test_items():
    add_to_cart("1", 2)
    add_to_cart("3", 3)
    return redirect(url_for("cart.view_cart"))

