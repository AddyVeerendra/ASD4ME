import os
import logging
from datetime import timedelta

from flask import Flask, render_template, url_for, redirect, jsonify, request, make_response
from flask_login import login_user, login_required, logout_user
from flask_wtf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies
from flask_cors import CORS

from Market import market_bp
from extensions import db, bcrypt, login_manager, migrate
from models import User

# Get the path of the database
file_path = os.path.abspath(os.getcwd()) + "/Database.db"

# Initialize the app
app = Flask(__name__)

# Set the app configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + file_path
app.config['SECRET_KEY'] = 'Study4Money'
app.config['JWT_SECRET_KEY'] = 'Token4TheW1N'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

# Initialize the database and other extensions
db.init_app(app)
migrate.init_app(app, db)
csrf = CSRFProtect(app)
bcrypt.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
jwt = JWTManager(app)
CORS(app)
app.register_blueprint(market_bp, url_prefix='/market')

# Set up logging
logging.basicConfig(level=logging.INFO)

app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = True
app.config['JWT_COOKIE_CSRF_PROTECT'] = True


@login_manager.user_loader
def load_user(user_id):
    logging.info(f"Loading user with id: {user_id}")
    return User.query.get(int(user_id))


class SignupForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'GET':
        return render_template('login.html', form=form)

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        logging.info(f"Attempting login for user: {form.username.data}")

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            logging.info(f"Password matched for user: {user.username}")
            access_token = create_access_token(identity=user.id)
            logging.info(f"Access token created for user: {user.username}")

            response = make_response(jsonify(success=True))
            set_access_cookies(response, access_token)
            logging.info(f"Access token set in cookies for user: {user.username}")

            return response

        logging.error(f"Login failed for user: {form.username.data}")
    return jsonify(success=False, message="Invalid credentials"), 401


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logging.info(f"User logging out: {get_jwt_identity()}")
    logout_user()
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        logging.info(f"New user created: {new_user.username}")
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)


@app.route('/some_secure_endpoint', methods=['GET'])
@jwt_required()
def secure_endpoint():
    current_user = get_jwt_identity()
    logging.info(f"Accessing secure endpoint by user: {current_user}")
    return jsonify(success=True, message=f"Hello, user {current_user}!")


@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Error occurred: {str(e)}")
    return jsonify(success=False, message=str(e)), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
