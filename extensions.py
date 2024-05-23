# extensions.py
from functools import wraps
from flask import current_app, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_migrate import Migrate

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.username not in current_app.config['ADMINS']:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

