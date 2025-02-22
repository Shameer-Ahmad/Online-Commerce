from flask import Blueprint, render_template

bp = Blueprint('landing', __name__, url_prefix='/')

@bp.route('/')
def landing_page():
    return render_template('landing/landing.html')