import secrets
from flask import Blueprint, session, request, g, render_template, redirect, url_for, redirect
from datetime import datetime, timedelta

from app.db import get_db, init_db
from app.auth import login_required

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

    stock = db.execute("SELECT UnitsInStock FROM Products WHERE ProductID = ?", (product_id,)).fetchone()
    if not stock:
        return redirect(url_for("cart.view_cart"))

    stock_limit = stock["UnitsInStock"]

    item = db.execute("SELECT quantity FROM Shopping_Cart WHERE product_id = ? AND shopper_id = ?", (product_id, shopper_id)).fetchone()

    if item:
            if item["quantity"] < stock_limit:
                db.execute("UPDATE Shopping_Cart SET quantity = quantity + 1 WHERE product_id = ? AND shopper_id = ?", (product_id, shopper_id))
    else:
        quantity = min(int(request.form.get("quantity", 1)), stock_limit)
        db.execute("INSERT INTO Shopping_Cart (shopper_id, product_id, quantity) VALUES (?, ?, ?)", (shopper_id, product_id, quantity))

    db.commit()
    return redirect(url_for("cart.view_cart"))
    
def calculate_total():
    items=get_items()
    return sum([item['price'] * item['quantity'] for item in items])

def get_items():
    db = get_db()
    shopper_id = check_id()
    cursor = db.execute("""SELECT Shopping_Cart.id, Shopping_Cart.quantity, Products.ProductName, Products.UnitPrice as price
                        FROM Shopping_Cart 
                        JOIN Products ON Shopping_Cart.product_id = Products.ProductID 
                        WHERE Shopping_Cart.shopper_id = ?
                        """, (shopper_id,))
    items = cursor.fetchall()

    print("Items at Checkout:", [dict(row) for row in items])
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

    item = db.execute("SELECT product_id, quantity FROM Shopping_Cart WHERE id = ? AND shopper_id = ?", (item_id, shopper_id)).fetchone()
    product_id = item["product_id"]

    stock = db.execute("SELECT UnitsInStock FROM Products WHERE ProductID = ?", (product_id,)).fetchone()
    if not stock:
        return redirect(url_for("cart.view_cart"))

    stock_limit = stock["UnitsInStock"]
        
    if item["quantity"] < stock_limit:
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

    db.execute("DELETE FROM Shopping_Cart WHERE shopper_id = ? AND created_at < ?", (shopper_id, one_month_ago))

    db.commit()
    return redirect(url_for("cart.view_cart"))

@bp.route("/checkout", methods=["POST"])
@login_required
def checkout():
    db = get_db()

    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    shopper_id = check_id()
    items = db.execute("""SELECT Shopping_Cart.product_id, Shopping_Cart.quantity, Products.UnitPrice AS price
                       FROM Shopping_Cart JOIN Products ON Shopping_Cart.product_id = Products.ProductID
                       WHERE Shopping_Cart.shopper_id = ?;
                       """, (shopper_id,)).fetchall()
    
    if not items:
        return redirect(url_for("cart.view_cart"))

    db.execute("INSERT INTO Orders (CustomerID, EmployeeID, OrderDate) VALUES (?, (select EmployeeID from Employees where LastName = 'WEB' and FirstName = 'WEB' limit 1), CURRENT_TIMESTAMP)", (session['user_id'],))
    order_id = db.execute("SELECT last_insert_rowid() AS id").fetchone()['id']

    for item in items:
        db.execute("""INSERT INTO order_items (order_id, user_id, shopper_id, product_id, quantity, price) 
                   VALUES (?, ?, ?, ?, ?, ?);
                   """, (order_id, session['user_id'], shopper_id, item['product_id'], item['quantity'], item['price']))
    
    db.execute("DELETE FROM Shopping_Cart WHERE shopper_id = ?", (shopper_id,))
    db.commit()
    
    clear()
    clean()

    return redirect(url_for("cart.shipping"))

@bp.route("/shipping", methods=["GET", "POST"])
def shipping():
    db = get_db()

    shippers = db.execute("SELECT ShipperID, CompanyName from Shippers").fetchall()

    if request.method == "POST":
        selected_shipper = request.form.get("shipper")
        session['selected_shipper'] = selected_shipper
        
        return redirect (url_for("cart.confirm"))

    return render_template("shipping.html", shippers=shippers)

@bp.route("/confirm")
def confirm():
    db = get_db()

    selected_shipper = session.get('selected_shipper')
    if selected_shipper:
        shipper = db.execute("SELECT CompanyName FROM Shippers WHERE ShipperID = ?", (selected_shipper,)).fetchone()
        if shipper:
            shipper_name = shipper["CompanyName"]
    
    order = db.execute("""SELECT Orders.OrderID, Orders.CustomerID, Orders.OrderDate, Orders.ShipAddress, Orders.ShipCity,
                       Orders.ShipPostalCode, Orders.ShipCountry
                       FROM Orders WHERE CustomerID = ? ORDER BY OrderDate DESC LIMIT 1;
                    """, (session['user_id'],)).fetchone()

    if not order:
        return redirect(url_for("cart.view_cart"))

    items = db.execute("""SELECT Products.ProductName AS Name, order_items.quantity AS Quantity, order_items.price AS Price
                        FROM order_items JOIN Products ON order_items.product_id = Products.ProductID
                        WHERE order_items.order_id = ?;
                    """, (order['OrderID'],)).fetchall()
    
    total = sum(item['quantity'] * item['price'] for item in items)

    return render_template("confirm.html", items=items, total=total, shipper_name=shipper_name)
