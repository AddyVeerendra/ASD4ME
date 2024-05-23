from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import InputRequired, Length, NumberRange
import logging
from wtforms.validators import DataRequired


from extensions import db
from models import StudyGuide, PendingStudyGuide  # Import the models from models.py

logging.basicConfig(level=logging.DEBUG)

market_bp = Blueprint('market_bp', __name__)

class ShareForm(FlaskForm):
    Class = StringField(validators=[InputRequired(), DataRequired(), Length(min=4, max=100)], render_kw={"placeholder": "Class"})
    UnitTopic = StringField(validators=[InputRequired(), DataRequired(), Length(min=4, max=100)], render_kw={"placeholder": "UnitTopic"})
    Price = IntegerField(validators=[InputRequired(), DataRequired(), NumberRange(min=0, max=1000)], render_kw={"placeholder": "Price"})
    Creator = StringField(validators=[DataRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Creator"})
    Link = StringField(validators=[InputRequired(), DataRequired(), Length(min=10, max=10000000)], render_kw={"placeholder": "Link"})
    submit = SubmitField('Sign Up')

@market_bp.route('/')
@login_required
def market_home():
    user = current_user
    items = StudyGuide.query.all()
    return render_template('market.html', user=user, items=items)

@market_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search_home():
    return render_template('Searchbar.html', user=current_user)


@market_bp.route('/share', methods=['GET', 'POST'])
@login_required
def share():
    form = ShareForm()
    form.Creator.data = current_user.username  # Assuming the Creator field is auto-filled with the current user's username
    if form.validate_on_submit():
        # Create a new PendingStudyGuide instance with form data
        new_pending_guide = PendingStudyGuide(
            Class=form.Class.data,
            UnitTopic=form.UnitTopic.data,
            Price=form.Price.data,
            Creator=form.Creator.data,
            Link=form.Link.data
        )
        # Add to the session and commit to the database
        db.session.add(new_pending_guide)
        db.session.commit()

        flash('Your study guide has been shared successfully and is pending approval!', 'success')
        return redirect(url_for('market_bp.market_home'))
    else:
        # Log the validation errors if needed
        logging.debug(f'Form validation failed: {form.errors}')

    return render_template('share.html', form=form, user=current_user)


@market_bp.route('/account', methods=['GET','POST'])
@login_required
def account_home():
    return render_template('Account.html', user=current_user)

@market_bp.route('/success')
def success():
    return "Successfully shared the study guide!"

def accept(id):
    if not current_user.is_admin:
        flash('You do not have access to this page.', 'danger')
        return redirect(url_for('market_bp.market_home'))

    pending_guide = PendingStudyGuide.query.get_or_404(id)
    new_guide = StudyGuide(Class=pending_guide.Class, UnitTopic=pending_guide.UnitTopic, Price=pending_guide.Price, Creator=pending_guide.Creator)
    db.session.add(new_guide)
    db.session.delete(pending_guide)
    db.session.commit()

    flash('Study guide accepted and added to the market.', 'success')
    return redirect(url_for('market_bp.admin'))
def reject(id):
    if not current_user.is_admin:
        flash('You do not have access to this page.', 'danger')
        return redirect(url_for('market_bp.market_home'))

    pending_guide = PendingStudyGuide.query.get_or_404(id)
    db.session.delete(pending_guide)
    db.session.commit()

    flash('Study guide rejected and removed from the pending list.', 'success')
    return redirect(url_for('market_bp.admin'))

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