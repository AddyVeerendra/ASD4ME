from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import InputRequired, Length, NumberRange
import logging
from wtforms.validators import DataRequired
from flask import render_template

from extensions import db
from models import StudyGuide, PendingStudyGuide  # Import the models from models.py

logging.basicConfig(level=logging.DEBUG)

# Blueprint for the market application
market_bp = Blueprint('market_bp', __name__)


class ShareForm(FlaskForm):
    """
    Form for users to share study guides.
    """
    Class = StringField(validators=[InputRequired(), DataRequired(), Length(min=4, max=100)],
                        render_kw={"placeholder": "Class"})
    UnitTopic = StringField(validators=[InputRequired(), DataRequired(), Length(min=4, max=100)],
                            render_kw={"placeholder": "UnitTopic"})
    Price = IntegerField(validators=[InputRequired(), DataRequired(), NumberRange(min=0, max=1000)],
                         render_kw={"placeholder": "Price"})
    Creator = StringField(validators=[DataRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Creator"})
    Link = StringField(validators=[InputRequired(), DataRequired(), Length(min=10, max=10000000)],
                       render_kw={"placeholder": "Link"})
    submit = SubmitField('Sign Up')


class AdminForm(FlaskForm):
    """
    Form for admin to approve or reject study guides.
    """
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    """
    Form for users to search study guides.
    """
    query = StringField('Query', validators=[DataRequired()])
    submit = SubmitField('Search')


@market_bp.route('/')
@login_required
def market_home():
    """
    Home page of the market application. Displays all study guides.
    """
    user = current_user
    items = StudyGuide.query.all()
    return render_template('market.html', user=user, items=items)


@market_bp.route('/share', methods=['GET', 'POST'])
@login_required
def share():
    """
    Page for users to share study guides.
    """
    form = ShareForm()
    form.Creator.data = current_user.username
    if form.validate_on_submit():
        # Create a new pending study guide
        new_pending_guide = PendingStudyGuide(
            Class=form.Class.data,
            UnitTopic=form.UnitTopic.data,
            Price=form.Price.data,
            Creator=form.Creator.data,
            Link=form.Link.data
        )

        db.session.add(new_pending_guide)
        db.session.commit()

        flash('Your study guide has been shared successfully and is pending approval!', 'success')
        return redirect(url_for('market_bp.market_home'))
    else:
        # Log the validation errors if needed
        logging.debug(f'Form validation failed: {form.errors}')

    return render_template('share.html', form=form, user=current_user)


@market_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account_home():
    """
    User's account page.
    """
    return render_template('Account.html', user=current_user)


@market_bp.route('/success')
def success():
    """
    Page displayed after a successful share.
    """
    return "Successfully shared the study guide!"


@market_bp.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_home():
    """
    Admin's home page. Displays pending study guides and allows admin to approve or reject them.
    """
    if not current_user.is_admin:
        flash('You do not have access to this page.', 'danger')
        return redirect(url_for('market_bp.market_home'))

    form = AdminForm()

    if request.method == 'POST' and form.validate_on_submit():
        action = request.form.get('action')
        guide_id = int(request.form.get('guide_id'))
        if action == 'approve':
            # Approve a pending study guide
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
                flash('Guide approved successfully!', 'success')
            else:
                flash('Guide not found!', 'danger')
        elif action == 'reject':
            # Reject a pending study guide
            rejected_guide = PendingStudyGuide.query.get(guide_id)
            if rejected_guide:
                db.session.delete(rejected_guide)
                db.session.commit()
                flash('Guide rejected successfully!', 'success')
            else:
                flash('Guide not found!', 'danger')
        else:
            flash('Form validation failed', 'danger')

        return redirect(url_for('market_bp.admin_home'))

    pending_guides = PendingStudyGuide.query.all()
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
    return render_template('searchbar.html', form=form, user=current_user)


@market_bp.route('/search/results')
@login_required
def results():
    """
    Page displaying search results.
    """
    query = request.args.get('query')
    if query:
        search = f"%{query}%"
        results = StudyGuide.query.filter(
            StudyGuide.Class.ilike(search) |
            StudyGuide.UnitTopic.ilike(search) |
            StudyGuide.Creator.ilike(search)
        ).order_by(StudyGuide.Price).all()
    else:
        results = []
    return render_template('results.html', results=results, query=query, user=current_user)