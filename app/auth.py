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
        db = get_db()
        user_id = request.form['username'].upper()  # Convert to uppercase for case-insensitive lookup
        password = request.form['password']

        # Check if user already exists
        existing_user = db.execute("SELECT userID FROM Authentication WHERE userID = ?", (user_id,)).fetchone()
        if existing_user:
            return "User ID already exists. Please choose another.", 400

        # Hash the password for security
        hashed_password = generate_password_hash(password)

        # Insert new user into Authentication table
        db.execute("INSERT INTO Authentication (userID, hashed_password) VALUES (?, ?)", (user_id, hashed_password))
        db.commit()
        return "Sucessfully registered!"

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        user_id = request.form['username'].upper()
        password = request.form['password']
        db = get_db()

        session_id = str(uuid.uuid4())  # Generate a new session 

        db.execute("UPDATE Authentication SET sessionID = ? WHERE userID = ?", (session_id, user_id))
        db.commit()

        # Update Flask session
        session["user_id"] = user_id  # Store user ID in session
        session["shopper_id"] = user_id  # Replace guest session ID with real user ID

        
        return redirect(url_for('landing.landing_page'))
        
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

""" @bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone() """

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

""" def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view """