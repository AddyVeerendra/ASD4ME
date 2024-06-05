"""
This file contains the extensions that will be initialized in the app factory. Initializations are handled here to
prevent errors
"""
# Importing necessary libraries
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Instantiating the extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()


