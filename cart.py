import secrets
from flask import Blueprint, session, request, g, render_template

bp = Blueprint("cart", __name__, url_prefix="/cart")

@bp.route("/")
def view_cart():
    return render_template("cart.html")
    
def get_db():
    import sqlite3
    if 'db' not in g:
        g.db = sqlite3.connect(':memory:')
        g.db.execute('CREATE TABLE cart (id INTEGER PRIMARY KEY, shopper_id TEXT, product_id TEXT, quantity INTEGER)')
        g.db.execute('CREATE TABLE products (id TEXT PRIMARY KEY, name TEXT, price REAL)')
        g.db.execute('INSERT INTO products (id, name, price) VALUES ("1", "Product 1", 10.0)')
        g.db.execute('INSERT INTO products (id, name, price) VALUES ("3", "Product 3", 30.0)')
    return g.db

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

def get_items():
    db = get_db()
    shopper_id = check_id()
    cursor = db.execute("SELECT cart.id, cart.quantity, products.name, products.price FROM cart JOIN products ON product_id = products.id WHERE cart.shopper_id = ?", (shopper_id,))
    items = cursor.fetchall()
    return [{'id': row[0], 'quantity': row[1], 'name': row[2], 'price': row[3]} for row in items]

@bp.route("/update_quantity/<int:item_id>", methods=["POST"])
def update_quantity(item_id):
    db = get_db()
    quantity = int(request.form.get("quantity", 1))
    db.execute("UPDATE cart SET quantity = ? WHERE id = ?", (quantity, item_id))
    db.commit()
    return "Quantity Updated.", 200

@bp.route("/remove/<int:item_id>")
def remove(item_id):
    db = get_db()
    db.execute("DELETE FROM cart WHERE id = ?", (item_id))
    db.commit()
    return "Item Removed.", 200
    
