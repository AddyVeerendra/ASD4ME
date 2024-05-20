from flask import Blueprint, render_template, request
from flask_login import login_required
from models import StudyGuide  # Import the models from models.py

market_bp = Blueprint('market_bp', __name__)

@market_bp.route('/')
@login_required
def market_home():
    items = StudyGuide.query.all()
    return render_template('market.html', items=items)

@market_bp.route('/search', methods=['GET', 'POST'])
def search():
    q = request.args.get('q')
    if q:
        results = StudyGuide.query.filter(StudyGuide.Class.ilike(f'%{q}%')).all()
    else:
        results = []
    return render_template('search_results.html', results=results)
