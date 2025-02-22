import secrets
from flask import Blueprint, session, request, g, render_template, redirect, url_for

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
                        JOIN products ON cart.product_id = Products.ProductID 
                        WHERE cart.shopper_id = ?
                        """, (shopper_id,))
    items = cursor.fetchall()
    return [{'id': row[0], 'quantity': row[1], 'name': row[2], 'price': row[3]} for row in items]

'''
@bp.route("/update_quantity/<int:item_id>", methods=["POST"])
def update_quantity(item_id):
    db = get_db()
    quantity = int(request.form.get("quantity", 1))
    db.execute("UPDATE cart SET quantity = ? WHERE id = ?", (quantity, item_id))
    db.commit()
    return "Quantity Updated.", 200
'''

# @bp.route("/remove/<int:item_id>")
def remove(product_id):
    db = get_db()
    db.execute("DELETE FROM cart WHERE id = ?", (product_id,))
    db.commit()
    return "Item Removed.", 200

@bp.route('/clean')
def clean():
    db = get_db()
    shopper_id = check_id()
    db.execute("DELETE FROM cart WHERE shopper_id = ? AND created_at < datetime('now', '-1 month')", (shopper_id,))
    db.commit()

@bp.route('/checkout', methods=['POST'])
def checkout():
    db = get_db()

    if 'user_id' not in session:
        return "Please Log In"
        #!! We will need to redirect to the log in page"

    shopper_id = check_id()
    items = db.execute("SELECT cart.product_id, cart.quantity, products.price FROM cart WHERE shopper_id = ?", (shopper_id,)).fetchall()

    # Get total cost of items
    cost = 0
    for item in items:
        cost += item['quantity'] * item['price']
    
    # Grabs the newest id label to make this new order have that id label
    order_id = db.execute("SELECT last_insert_rowid() AS id").fetchone()['id']

    # Insert every item from the cart associated with this user into the order_items table
    for item in items:
        db.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)", (order_id, item['product_id'], item['quantity'], item['price'] ))
    
    # Delete that users old items from the cart
    db.execute("DELETE FROM cart WHERE shopper_id = ?", (shopper_id))
    
    db.commit()

    # Delete anything from the entire cart where the product has been there for over a month
    clean()


@bp.route("/add_test_items")
def add_test_items():
    add_to_cart("1", 2)
    add_to_cart("3", 3)
    return redirect(url_for("cart.view_cart"))

@bp.route("/debug_cart")
def debug_cart():
    db = get_db()
    items = db.execute("SELECT * FROM cart").fetchall()
    return str([dict(row) for row in items])
