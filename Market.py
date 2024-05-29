"""
Market.py is the main file for the market application. It contains the following functions:
    - market_home: Home page of the market application. Displays basic user info such as wallet balance, and allows
    navigation to other parts of the website. Also displays all study guides available for purchase.
    - share: Page for users to share study guides. Users enter the necessary information to share a study guide in
    share.html
    - account_home: User's account page. Displays account info such as wallet balance and cart. Allows users to purchase
    cart info
    - admin_home: Admin's home page. Displays pending study guides and allows admin to approve or reject them.
    - search: Page for users to search study guides.
    - results: Page displaying search results.
"""
from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import InputRequired, Length, NumberRange
import logging
from wtforms.validators import DataRequired
from flask import render_template

from extensions import db  # Import the database object from extensions.py
from models import study_guide, pending_study_guide, Cart, CartItem  # Import the models from models.py

# Used for logging changes in consoles
logging.basicConfig(level=logging.DEBUG)

# Blueprint for the market application
market_bp = Blueprint('market_bp', __name__)

'''
Things to know:
@login_required: Checks if the user is logged in. If not, the page does not open.
FlaskForm: Type of form defined by flask_wtf in imports
StringField: Field for users to enter text
SubmitField: Button that receives submit input
InputRequired: Checks if the field is filled
Length: Checks if the length of the field is within a certain range
NumberRange: Checks if the number is within a certain range
'''


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
@login_required
def market_home():
    """
    Home page of the market application. Displays basic user info such as wallet balance, and allows navigation to other
    parts of the website. Also displays all study guides available for purchase.
    """
    user = current_user
    items = study_guide.query.all()
    return render_template('market.html', user=user, items=items)


@market_bp.route('/share', methods=['GET', 'POST'])
@login_required
def share():
    """
    Page for users to share study guides. Users enter the necessary information to share a study guide in share.html
    """
    # Initialize form
    form = ShareForm()
    # Autofill creator field with username of account
    form.Creator.data = current_user.username
    # Check for form validation
    if form.validate_on_submit():
        # Create a new pending study guide and fill in data using input from forms
        new_pending_guide = pending_study_guide(
            Class=form.Class.data,
            UnitTopic=form.UnitTopic.data,
            Price=form.Price.data,
            Creator=form.Creator.data,
            Link=form.Link.data
        )
        # Add the new pending study guide to the database
        db.session.add(new_pending_guide)
        # Commit the changes to the study guide
        db.session.commit()
    # Render share.html for the users to successfully share
    return render_template('share.html', form=form, user=current_user)


@market_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account_home():
    """
    User's account page. Displays account info such as wallet balance and cart. Allows users to purchase cart info
    """
    # Render Account.html for the users to see their account info
    return render_template('Account.html', user=current_user)


@market_bp.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_home():
    """
    Admin's home page. Displays pending study guides and allows admin to approve or reject them.
    """
    # Check if the user is an admin. If not, redirect to the market home page (is_admin is a boolean in user database)
    if not current_user.is_admin:
        return redirect(url_for('market_bp.market_home'))
    # Initialize form
    form = AdminForm()
    # Check for form validation
    if request.method == 'POST' and form.validate_on_submit():
        # Get the action and guide_id from the form (Found in the hidden input fields in admin.html)
        action = request.form.get('action')
        # Receive the guide_id from the form
        guide_id = int(request.form.get('guide_id'))
        # Check if the action is approve
        if action == 'approve':
            # Create a new approved study guide using data from the pending study guide
            approved_guide = pending_study_guide.query.get(guide_id)
            if approved_guide:
                new_guide = study_guide(
                    Class=approved_guide.Class,
                    UnitTopic=approved_guide.UnitTopic,
                    Price=approved_guide.Price,
                    Creator=approved_guide.Creator,
                    Link=approved_guide.Link
                )
                # Add the new study guide to the database
                db.session.add(new_guide)
                # Delete the old study guide from the database
                db.session.delete(approved_guide)
                # Commit changes to the database
                db.session.commit()
        elif action == 'reject':
            # Reject a pending study guide
            rejected_guide = pending_study_guide.query.get(guide_id)
            if rejected_guide:
                db.session.delete(rejected_guide)
                db.session.commit()
                flash('Guide rejected successfully!', 'success')
            else:
                flash('Guide not found!', 'danger')
        else:
            flash('Form validation failed', 'danger')

        return redirect(url_for('market_bp.admin_home'))

    pending_guides = pending_study_guide.query.all()
    return render_template('admin.html', pending_guides=pending_guides, user=current_user, form=form)


@market_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    """
    Page for users to search study guides.
    """
    form = SearchForm()
    if form.validate_on_submit():
        query = form.query.data
        return redirect(url_for('market_bp.results', query=query))
    return render_template('Searchbar.html', form=form, user=current_user)


@market_bp.route('/results', methods=['GET', 'POST'])
@login_required
def results():
    form = FlaskForm()  # Create an instance of your form class

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_to_cart':
            study_guide_id = request.form.get('study_guide_id')
            if study_guide_id:
                StudyGuide = study_guide.query.get(study_guide_id)
                if StudyGuide:
                    if not current_user.cart:
                        cart = Cart(user_id=current_user.id)
                        db.session.add(cart)
                        db.session.commit()
                    else:
                        cart = current_user.cart
                    cart_item = CartItem.query.filter_by(cart_id=cart.id, study_guide_id=study_guide_id).first()
                    if cart_item:
                        cart_item.quantity += 1
                    else:
                        cart_item = CartItem(cart_id=cart.id, study_guide_id=study_guide_id, quantity=1)
                        db.session.add(cart_item)

                    db.session.commit()
                    flash('Item added to cart successfully!', 'success')
                else:
                    flash('Study guide not found.', 'danger')
            else:
                flash('Invalid request.', 'danger')

    query = request.args.get('query')
    results = []
    if query:
        results = study_guide.query.filter(
            (study_guide.Class.ilike(f'%{query}%')) |
            (study_guide.UnitTopic.ilike(f'%{query}%')) |
            (study_guide.Creator.ilike(f'%{query}%'))
        ).all()

    return render_template('results.html', query=query, results=results, form=form)