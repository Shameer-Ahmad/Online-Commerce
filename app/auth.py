import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.execute('SELECT ProductName FROM Products ORDER BY RANDOM() LIMIT 1')
        product = cursor.fetchone()
        product_name = product['ProductName'] if product else 'No product found'
        
        return "Your username is {}<br>Your password is {}<br>Accessing a random product from northwind: {}".format(username, password, product_name)
        
        """ db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)
    """
    return render_template('auth/login.html') 


@bp.route('/database')
def database():
    db = get_db()

    # Fetch first 10 products
    cursor = db.execute('SELECT * FROM Products LIMIT 10')
    products = cursor.fetchall()

    # Fetch first 10 categories
    cursor = db.execute('SELECT * FROM Categories LIMIT 10')
    categories = cursor.fetchall()

    # Convert image blobs to Base64
    categories_list = []
    for category in categories:
        category_dict = dict(category)
        
        import base64
        if category_dict["Picture"]:  # If Picture exists
            category_dict["Picture"] = base64.b64encode(category_dict["Picture"]).decode('utf-8')

        categories_list.append(category_dict)

    return render_template('auth/database.html', products=products, categories=categories)

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view