"""
ASD4ME.py is the main file of the project. It contains the main code for the project, and also has the blueprint
for the market. The blueprint is registered with the app, and the app is run on the server. This file is where
database connections are initialized, and where users first interact with the website. The program contains these
functions:
        - home(): This function renders the index.html template, the homepage of the website
        - login(): This function renders the login.html template, and allows users to log in to the website using forms.
        - logout(): This function logs the user out of the website.
        - signup(): This function renders the signup.html template, allowing users to sign up for the website via forms.
        - load_user(): This function loads the user's id from the database.
        - app.run(): This function runs the app on the server.
"""

# os import to retrieve database path
import os

# General flask imports
from flask import Flask, render_template, url_for, redirect
from flask_login import login_user, login_required, logout_user
from flask_wtf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length

# Import the market blueprint
from Market import market_bp
# Import extensions such as db and bcrypt from extensions.py
from extensions import db, bcrypt, login_manager, migrate
# Import the User model from models.py
from models import User

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

# Get the path of the database
file_path = os.path.abspath(os.getcwd()) + "/Database.db"

# Initialize the app
app = Flask(__name__)
# Set the app configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + file_path
# Set the app configuration
app.config['SECRET_KEY'] = 'Study4Money'
# Initialize the database
db.init_app(app)
# Initialize the migration system
migrate.init_app(app, db)
# Initialize the CSRF protection
csrf = CSRFProtect(app)

# Initialize bcrypt
bcrypt.init_app(app)
# Initialize the login manager
login_manager.init_app(app)
# Set the login view
login_manager.login_view = 'login'

# Register the market blueprint with the app to gain access to market.py
app.register_blueprint(market_bp, url_prefix='/market')


@login_manager.user_loader
def load_user(user_id):
    """
    This function loads the user's id by querying the database and returning the id when found.
    """
    # return the user's database id
    return User.query.get(int(user_id))


class SignupForm(FlaskForm):
    """
    Form for users to create an account for the website by entering a username and password, and submitting the form.
    """
    # username: Field for users to enter their username
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    # password: Field for users to enter their password
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    # submit: Button for users to submit the form
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    """
    Form for users to log in to the website by entering a username and password, and submitting the form.
    """
    # username: Field for users to enter their username
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    # password: Field for users to enter their password
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    # submit: Button for users to submit the form
    submit = SubmitField('Login')


@app.route('/')
def home():
    """
    This function renders the index.html template, the homepage of the website.
    """
    # Render the index.html template
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    This function renders the login.html template, and allows users to log in to the website using forms.
    """
    # Initialize LoginForm
    form = LoginForm()
    # Check if the form is validated
    if form.validate_on_submit():
        # Query the database for the user
        user = User.query.filter_by(username=form.username.data).first()
        # Check if the user exists and the password is correct
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # Log the user in, starting their session
            login_user(user)
            # Redirect to the market blueprint's home
            return redirect(url_for('market_bp.market_home'))
    # Render the login.html template
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """
    This function logs the user out of the website, ending their session.
    """
    # Log the user out, ending their session
    logout_user()
    # Redirect to the login page
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    This function renders the signup.html template, allowing users to create an account for the website via forms.
    """
    # Initialize SignupForm
    form = SignupForm()
    # Check if the form is validated
    if form.validate_on_submit():
        # Create a new hashed password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # Create a new user with the username and hashed password
        new_user = User(username=form.username.data, password=hashed_password)
        # Add the new user to the database
        db.session.add(new_user)
        # Commit the changes to the database
        db.session.commit()
        # Redirect to the login page
        return redirect(url_for('login'))
    # Render the signup.html template
    return render_template('signup.html', form=form)


# Run the app on the server
if __name__ == '__main__':
    # Create all the tables in the database
    with app.app_context():
        db.create_all()
    # Run the app on the server
    app.run(host='0.0.0.0', port=5000)
