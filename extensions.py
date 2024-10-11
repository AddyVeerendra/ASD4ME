"""
This file contains the extensions that will be initialized in the app factory. Initializations are handled here to
prevent errors
"""
# Importing necessary libraries
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask import request, jsonify
import jwt

# Instantiating the extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(data, *args, **kwargs)
    return decorated


