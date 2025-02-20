import secrets
from flask import Flask, session, g
from cart import check_id, add_to_cart, get_items, get_db, remove

app = Flask(__name__)
app.secret_key = 'secretkey'

def get_db():
    import sqlite3
    if 'db' not in g:
        g.db = sqlite3.connect(':memory:')
        g.db.execute('CREATE TABLE cart (id INTEGER PRIMARY KEY, shopper_id TEXT, product_id TEXT, quantity INTEGER)')
        g.db.execute('CREATE TABLE products (id TEXT PRIMARY KEY, name TEXT, price REAL)')
        g.db.execute('INSERT INTO products (id, name, price) VALUES ("1", "Product 1", 10.0)')
        g.db.execute('INSERT INTO products (id, name, price) VALUES ("3", "Product 3", 30.0)')
    return g.db

# Mock session setup
with app.app_context():
    with app.test_request_context():
        session['shopper_id'] = secrets.token_hex(16)
        db = get_db()
        g.db = db

        # Test check_id function
        print("Shopper ID:", check_id())

        # Test add_to_cart function
        add_to_cart("1", 2)
        print("Added to cart")

        add_to_cart("3", 4)
        print("Added to cart again")

        # Test get_items function
        items = get_items()
        print(items)

        # Test remove function
        remove("1")
        print("Removed from cart")

        # Test get_items function
        updated_items = get_items()
        print(updated_items)