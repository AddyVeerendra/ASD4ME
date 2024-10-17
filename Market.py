# General flask imports
import logging

from flask import Blueprint, redirect, url_for, request
from flask import render_template
from flask_jwt_extended import jwt_required, get_jwt_identity, unset_jwt_cookies
from flask_login import logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange

# Database imports
from extensions import db
# Model imports
from models import StudyGuide, PendingStudyGuide, Cart, CartItem, Inventory, User

# Blueprint for the market application (Accessed by ASD4ME.py and HTML templates)
market_bp = Blueprint('market_bp', __name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ShareForm(FlaskForm):
    """
    Form for users to share study guides. Users enter the class, unit/topic, price, creator, and link to the study guide
    FlaskForm: Type of form defined by flask_wtf in imports
    """
    # Class: Class study guide is about
    Class = StringField(validators=[InputRequired(), DataRequired(), Length(min=4, max=100)],
                        render_kw={"placeholder": "Class"})
    # Unit Topic: Topic study guide is about
    UnitTopic = StringField(validators=[InputRequired(), DataRequired(), Length(min=4, max=100)],
                            render_kw={"placeholder": "UnitTopic"})
    # Price: Price of study guide
    Price = IntegerField(validators=[InputRequired(), DataRequired(), NumberRange(min=0, max=1000)],
                         render_kw={"placeholder": "Price"})
    # Creator: Author of the study guide (Field autofilled with username of account)
    Creator = StringField(validators=[DataRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Creator"})
    # Link: Link to the study guide
    Link = StringField(validators=[InputRequired(), DataRequired(), Length(min=10, max=10000000)],
                       render_kw={"placeholder": "Link"})
    # Submit: Button that receives submit input
    submit = SubmitField('Sign Up')


class AdminForm(FlaskForm):
    """
    Form for admin to approve or reject study guides. Admins can submit a form to approve or reject a study guide.
    FlaskForm: Type of form defined by flask_wtf in imports
    """
    # Submit: Button that receives submit input
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    """
    Form for users to search study guides. Users use a searchbar to search for study guides
    """
    # query: The string users use to search
    query = StringField('Query', validators=[DataRequired()])
    # submit: Button that receives submit input
    submit = SubmitField('Search')



@market_bp.route('/')
@jwt_required()
def market_home():
    user_id = get_jwt_identity()
    logging.info(f"JWT Identity: {user_id}")
    user = User.query.filter_by(id=user_id).first()
    items = StudyGuide.query.all()
    return render_template('market.html', user=user, items=items)



@market_bp.route('/share', methods=['GET', 'POST'])
@jwt_required()
def share():
    user = User.query.filter_by(id=get_jwt_identity()).first()
    form = ShareForm()
    form.Creator.data = user.username
    if form.validate_on_submit():
        new_pending_guide = PendingStudyGuide(
            Class=form.Class.data,
            UnitTopic=form.UnitTopic.data,
            Price=form.Price.data,
            Creator=form.Creator.data,
            Link=form.Link.data
        )
        db.session.add(new_pending_guide)
        db.session.commit()
        return redirect(url_for('market_bp.market_home'))
    return render_template('share.html', form=form, user=user)


@market_bp.route('/account', methods=['GET', 'POST'])
@jwt_required()
def account_home():
    user = User.query.filter_by(id=get_jwt_identity()).first()
    form = FlaskForm()
    cart = user.cart
    if cart:
        cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
    else:
        cart_items = []
    if request.method == 'POST':
        item_id = request.form.get('item_id')
        if item_id:
            cart_item = CartItem.query.get(item_id)
            if cart_item and cart_item.cart.user_id == user.id:
                db.session.delete(cart_item)
                db.session.commit()
        return redirect(url_for('market_bp.account_home'))

    inventory_items = Inventory.query.filter_by(user_id=user.id).all()
    return render_template('account.html', wallet=user.wallet, cart_items=cart_items, inventory=inventory_items, form=form)


@market_bp.route('/finalize_purchase', methods=['POST'])
@jwt_required()
def finalize_purchase():
    user = User.query.filter_by(id=get_jwt_identity()).first()
    cart = user.cart
    total_cost = sum(item.study_guide.Price * item.quantity for item in cart.items)
    if user.wallet < total_cost:
        return redirect(url_for('market_bp.account_home'))
    for item in cart.items:
        study_guide = item.study_guide
        creator = User.query.filter_by(username=study_guide.Creator).first()
        if creator:
            creator.wallet += study_guide.Price * item.quantity
        for _ in range(item.quantity):
            inventory_item = Inventory(user_id=user.id, study_guide_id=study_guide.id)
            db.session.add(inventory_item)

    user.wallet -= total_cost
    CartItem.query.filter_by(cart_id=cart.id).delete()
    db.session.delete(cart)
    db.session.commit()

    return redirect(url_for('market_bp.account_home'))


@market_bp.route('/admin', methods=['GET', 'POST'])
@jwt_required()
def admin_home():
    user = User.query.filter_by(id=get_jwt_identity()).first()
    if not user.is_admin:
        return redirect(url_for('market_bp.market_home'))
    form = AdminForm()
    if request.method == 'POST' and form.validate_on_submit():
        action = request.form.get('action')
        guide_id = int(request.form.get('guide_id'))
        if action == 'approve':
            approved_guide = PendingStudyGuide.query.get(guide_id)
            if approved_guide:
                new_guide = StudyGuide(
                    Class=approved_guide.Class,
                    UnitTopic=approved_guide.UnitTopic,
                    Price=approved_guide.Price,
                    Creator=approved_guide.Creator,
                    Link=approved_guide.Link
                )
                db.session.add(new_guide)
                db.session.delete(approved_guide)
                db.session.commit()
        elif action == 'reject':
            rejected_guide = PendingStudyGuide.query.get(guide_id)
            db.session.delete(rejected_guide)
            db.session.commit()
        return redirect(url_for('market_bp.admin_home'))
    pending_guides = PendingStudyGuide.query.all()
    return render_template('admin.html', pending_guides=pending_guides, user=user, form=form)


@market_bp.route('/search', methods=['GET', 'POST'])
@jwt_required()
def search():
    user = User.query.filter_by(id=get_jwt_identity()).first()
    form = SearchForm()
    if form.validate_on_submit():
        query = form.query.data
        return redirect(url_for('market_bp.results', query=query))
    return render_template('searchbar.html', form=form, user=user)


@market_bp.route('/search/results', methods=['GET', 'POST'])
@jwt_required()
def results():
    user = User.query.filter_by(id=get_jwt_identity()).first()
    form = FlaskForm()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_to_cart':
            study_guide_id = request.form.get('study_guide_id')
            if study_guide_id:
                study_guide = StudyGuide.query.get(study_guide_id)
                if study_guide:
                    if not user.cart:
                        cart = Cart(user_id=user.id)
                        db.session.add(cart)
                        db.session.commit()
                    else:
                        cart = user.cart
                    cart_item = CartItem.query.filter_by(cart_id=cart.id, study_guide_id=study_guide_id).first()
                    if cart_item:
                        cart_item.quantity += 0
                    else:
                        cart_item = CartItem(cart_id=cart.id, study_guide_id=study_guide_id, quantity=1)
                        db.session.add(cart_item)
                    db.session.commit()
    query = request.args.get('query')
    if query:
        results = StudyGuide.query.filter(
            (StudyGuide.Class.ilike(f'%{query}%')) |
            (StudyGuide.UnitTopic.ilike(f'%{query}%')) |
            (StudyGuide.Creator.ilike(f'%{query}%'))
        ).all()
    else:
        results = []
    return render_template('results.html', query=query, results=results, form=form)


@market_bp.route('/logout')
@jwt_required()
def logout():
    # Log the logout event
    user_id = get_jwt_identity()
    logger.info(f'User {user_id} is logging out.')

    # Log out the user from Flask-Login session
    logout_user()
    logger.info(f'User {user_id} has been logged out of Flask-Login.')

    # Prepare the response
    response = redirect(url_for('home'))

    # Unset JWT cookies from the response
    unset_jwt_cookies(response)
    logger.info(f'JWT cookies cleared for user {user_id}.')

    return response
