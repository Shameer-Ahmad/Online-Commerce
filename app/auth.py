import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import uuid

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
            return redirect(url_for('landing.landing_page'))

        flash(error)

        # Update Flask session
        old_shopper_id = session.get("shopper_id")
        session["user_id"] = username  # Store user ID in session
        session["shopper_id"] = username

        db.execute("""
                   UPDATE Shopping_Cart SET shopper_id = ? WHERE shopper_id = ?
                   """, (username, old_shopper_id))
        db.commit()
        
    return render_template('auth/login.html') 


@bp.route('/database')
def database():
    db = get_db()

    # Fetch first 10 products
    cursor = db.execute('SELECT * FROM Orders LIMIT 10')
    products = cursor.fetchall()

    # Fetch first 10 categories
    cursor = db.execute('SELECT * FROM Employees LIMIT 10')
    categories = cursor.fetchall()

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
    return redirect(url_for('landing.landing_page'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view