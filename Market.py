# Market.py
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from ASD4ME import db, User, StudyGuide  # Import necessary models

market_bp = Blueprint('market_bp', __name__)

@market_bp.route('/')
@login_required
def market_home():
    user = current_user
    items = StudyGuide.query.all()
    return render_template('market.html', user=user, items=items)

@market_bp.route('/search')
@login_required
def search_home():
    return render_template('Searchbar.html', user=current_user)

# Below commented lines need to be added and edited afterwards
"""
@market_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    q = request.args.get('q')
    if q:
        results = StudyGuide.query.filter(StudyGuide.Class.ilike(f'%{q}%')).all()
    else:
        results = []
    return render_template('search_results.html', results=results, user=current_user)
"""