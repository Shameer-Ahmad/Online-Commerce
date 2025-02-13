import secrets
from flask import session, request, g

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
    return db.execute("select cart.id, cart.quantity, products.name, products.price from cart join products on product_id = products.id where cart.shopper_id = ?", (shopper_id), ).fetchall()

