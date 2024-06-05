"""
Market.py is a blueprint that contains all the routes and functions for the market application. It is accessed by
ASD4ME.py when necessary, and contains many market operations such as purchasing and sharing. The functions in this
file are:
        - market_home(): Home page of the market application. Displays basic user info such as wallet balance, and
        allows navigation to other parts of the website. Also displays all study guides available for purchase.
        - share(): Page for users to share study guides. Users enter the necessary information to share a study guide in
        share.html
        - account_home(): account_home is the user's account page, which displays account info such as wallet balance
        and cart. This function gives users the option to remove study guides, finalize their cart purchases, and view
        items in their inventory.
        - finalize_purchase(): finalize_purchase allows users to finish adding the items in their cart to their
        inventory, and accordingly checks and subtracts from wallet balance. If the wallet_balance is high enough, the
        transaction is completed and items are moved to their inventory. Otherwise, it does not go through.
        - admin_home(): Admin home page. Displays pending study guides and allows admin to approve or reject them.
        - search(): Page for users to search study guides. Users enter a string in searchbar.html and the string is
        retrieved and stored
        - results(): results allows users to view the results of their search query, and add study guides to their cart
        - logout(): logout logs the user out of the website.
"""

# General flask imports
from flask import Blueprint, redirect, url_for, request
from flask import render_template
from flask_login import login_required, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from wtforms.validators import InputRequired, Length, NumberRange

# Database imports
from extensions import db
# Model imports
from models import StudyGuide, PendingStudyGuide, Cart, CartItem, Inventory, User

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

# Blueprint for the market application (Accessed by ASD4ME.py and HTML templates)
market_bp = Blueprint('market_bp', __name__)


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
    # Get the current user
    user = current_user
    # Get all study guides
    items = StudyGuide.query.all()
    # Render market.html for the users to see the market home page
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
        new_pending_guide = PendingStudyGuide(
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
        # Redirect to the market home page after sharing
        return redirect(url_for('market_bp.market_home'))
    # Render share.html for the users to successfully share
    return render_template('share.html', form=form, user=current_user)


@market_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account_home():
    """
    account_home is the user's account page, which displays account info such as wallet balance and cart. This function
    gives users the option to remove study guides, finalize their cart purchases, and view items in their inventory.
    """
    # Initialize the form
    form = FlaskForm()
    # Fetch current user's cart
    cart = current_user.cart
    # Query user's cart database to get all the items
    if cart:
        cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
    else:
        cart_items = []
    # Check for a request in account.html
    if request.method == 'POST':
        # Get the item_id from the form
        item_id = request.form.get('item_id')
        # Check if the item_id is valid
        if item_id:
            # Get the item_id of the study guide in the cart
            cart_item = CartItem.query.get(item_id)
            # Check if the cart_item exists, and whether the current user's id matches the user_id stored in cart_item
            if cart_item and cart_item.cart.user_id == current_user.id:
                # Delete the cart_item from the database
                db.session.delete(cart_item)
                # Commit changes to the database
                db.session.commit()
        # Redirect to the account page after removed
        return redirect(url_for('market_bp.account_home'))

    # Fetch all the user's inventory items from their inventory database
    inventory_items = Inventory.query.filter_by(user_id=current_user.id).all()
    # Render the account.html template (Setting wallet, cart_items, inventory_items, and the form to what is necessary)
    return render_template('account.html', wallet=current_user.wallet, cart_items=cart_items, inventory=inventory_items,
                           form=form)


@market_bp.route('/finalize_purchase', methods=['POST'])
@login_required
def finalize_purchase():
    """
    finalize_purchase allows users to finish adding the items in their cart to their inventory, and accordingly checks
    and subtracts from wallet balance. If the wallet_balance is high enough, the transaction is completed and items are
    moved to their inventory. Otherwise, it does not go through.
    """
    # Fetch the current user's cart
    cart = current_user.cart
    # Calculate the total cost of all the items in the cart
    total_cost = sum(item.study_guide.Price * item.quantity for item in cart.items)
    # Check if the user does not have enough money in their wallet
    if current_user.wallet < total_cost:
        # Redirect to the account page if they don't have enough money
        return redirect(url_for('market_bp.account_home'))
    # For each item in the cart
    for item in cart.items:
        # Get the corresponding study guide from the item
        study_guide = item.study_guide
        # Find the creator using info from the study guide
        creator = User.query.filter_by(username=study_guide.Creator).first()
        # If the creator exists, add the price of the study guide to their wallet
        if creator:
            creator.wallet += study_guide.Price * item.quantity
        # For each item in the cart
        for _ in range(item.quantity):
            # Create a new inventory item for the user
            inventory_item = Inventory(user_id=current_user.id, study_guide_id=study_guide.id)
            # Add the inventory item to the database
            db.session.add(inventory_item)

    # Subtract the total cost from the user's wallet
    current_user.wallet -= total_cost

    # Delete all items in the cart
    CartItem.query.filter_by(cart_id=cart.id).delete()

    # Delete the cart itself
    db.session.delete(cart)
    # Commit changes to the database
    db.session.commit()

    # Redirect to the account page
    return redirect(url_for('market_bp.account_home'))


@market_bp.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_home():
    """
    Admin home page. Displays pending study guides and allows admin to approve or reject them.
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
            approved_guide = PendingStudyGuide.query.get(guide_id)
            if approved_guide:
                new_guide = StudyGuide(
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
            rejected_guide = PendingStudyGuide.query.get(guide_id)
            # Delete the rejected study guide from the database
            db.session.delete(rejected_guide)
            # Commit changes to the database
            db.session.commit()
        # Redirect to the admin page
        return redirect(url_for('market_bp.admin_home'))
    # Retrieve all pending study guides
    pending_guides = PendingStudyGuide.query.all()
    # Render admin.html for the admin to approve or reject study guides
    return render_template('admin.html', pending_guides=pending_guides, user=current_user, form=form)


@market_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    """
    Page for users to search study guides. Users enter a string in searchbar.html and the string is retrieved and stored
    """
    # Initialize form
    form = SearchForm()
    # Check for form validation
    if form.validate_on_submit():
        # Get the query from the form
        query = form.query.data
        # Redirect to the results page using the query
        return redirect(url_for('market_bp.results', query=query))
    # Render searchbar.html for the users to search for study guides
    return render_template('searchbar.html', form=form, user=current_user)


@market_bp.route('/search/results', methods=['GET', 'POST'])
@login_required
def results():
    """
    results allows users to view the results of their search query, and add study guides to their cart
    """
    # Initialize form
    form = FlaskForm()
    # Check whether the request went through
    if request.method == 'POST':
        # Get the action from the form
        action = request.form.get('action')
        # Check if the action is add_to_cart in results.html (Obtained from clicking the "add-to-cart" button
        if action == 'add_to_cart':
            # Get the study guide id from the form
            study_guide_id = request.form.get('study_guide_id')
            # Check if the study guide id is valid
            if study_guide_id:
                # Get the study guide from the database
                study_guide = StudyGuide.query.get(study_guide_id)
                # Check if the study guide exists
                if study_guide:
                    # Check if the user has a cart.
                    if not current_user.cart:
                        # If the user does not have a cart, create a new cart
                        cart = Cart(user_id=current_user.id)
                        # Add the cart to the database
                        db.session.add(cart)
                        # Commit changes to the database
                        db.session.commit()
                    # If the user has a cart, get the cart
                    else:
                        cart = current_user.cart
                    # Check if the item is already in the cart
                    cart_item = CartItem.query.filter_by(cart_id=cart.id, study_guide_id=study_guide_id).first()
                    # If the item is in the cart, do nothing
                    if cart_item:
                        cart_item.quantity += 0
                    # If the item is not in the cart, add the item to the cart
                    else:
                        # Create a new cart item
                        cart_item = CartItem(cart_id=cart.id, study_guide_id=study_guide_id, quantity=1)
                        # Add the cart item to the database
                        db.session.add(cart_item)
                    # Commit changes to the database
                    db.session.commit()
    # Get the query from the form
    query = request.args.get('query')
    # Get the study guides from the database using the query
    if query:
        # Get the study guides from the database by filtering using the query
        results = StudyGuide.query.filter(
            (StudyGuide.Class.ilike(f'%{query}%')) |
            (StudyGuide.UnitTopic.ilike(f'%{query}%')) |
            (StudyGuide.Creator.ilike(f'%{query}%'))
        ).all()
    else:
        # If there is no query, set results to an empty list
        results = []

    # Render the results.html template for the users to view the results of their search query
    return render_template('results.html', query=query, results=results, form=form)


@market_bp.route('/logout')
@login_required
def logout():
    """
    This function logs the user out of the website, ending their session.
    """
    # Log the user out
    logout_user()
    # Redirect to the home page
    return redirect(url_for('home'))
