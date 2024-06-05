"""
This file contains the models for the database. The models are used to create the tables in the database.
"""
# Importing necessary libraries
from extensions import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    """
    This class creates the User table in the database. The User table contains the following columns:
    - id: The primary key of the table
    - username: The username of the user
    - password: The password of the user
    - wallet: The wallet balance of the user
    - is_admin: A boolean value that indicates if the user is an admin
    - cart: A relationship to the Cart table
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    wallet = db.Column(db.Integer, nullable=False, default=0)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    cart = db.relationship('Cart', uselist=False, backref='user')


class StudyGuide(db.Model):
    """
    This class creates the StudyGuide table in the database. The StudyGuide table contains the following columns:
    - id: The primary key of the table
    - Class: The class of the study guide
    - UnitTopic: The unit/topic of the study guide
    - Price: The price of the study guide
    - Creator: The creator of the study guide
    - Link: The link to the study guide
    """
    id = db.Column(db.Integer, primary_key=True)
    Class = db.Column(db.String(20), nullable=False)
    UnitTopic = db.Column(db.String(20), nullable=False)
    Price = db.Column(db.Integer, nullable=False)
    Creator = db.Column(db.String(20), nullable=False)
    Link = db.Column(db.String(100), nullable=False)


class PendingStudyGuide(db.Model):
    """
    This class creates the PendingStudyGuide table in the database. PendingStudyGuide is different from "StudyGuide"
    because it is used in a different situation. The PendingStudyGuide table contains the following columns:
    - id: The primary key of the table
    - Class: The class of the study guide
    - UnitTopic: The unit/topic of the study guide
    - Price: The price of the study guide
    - Creator: The creator of the study guide
    - Link: The link to the study guide
    """
    id = db.Column(db.Integer, primary_key=True)
    Class = db.Column(db.String(20), nullable=False)
    UnitTopic = db.Column(db.String(20), nullable=False)
    Price = db.Column(db.Integer, nullable=False)
    Creator = db.Column(db.String(20), nullable=False)
    Link = db.Column(db.String(100), nullable=False)


class Cart(db.Model):
    """
    This class creates the Cart table in the database. The Cart table contains the following columns:
    - id: The primary key of the table
    - user_id: The foreign key to the User table
    - items: A relationship to the CartItem table
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items = db.relationship('CartItem', backref='cart', lazy=True)


class CartItem(db.Model):
    """
    This class creates the CartItem table in the database. The CartItem table contains the following columns:
    - id: The primary key of the table
    - cart_id: The foreign key to the Cart table
    - study_guide_id: The foreign key to the StudyGuide table
    - quantity: The quantity of the study guide in the cart
    - study_guide: A relationship to the StudyGuide table
    """
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)
    study_guide_id = db.Column(db.Integer, db.ForeignKey('study_guide.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    study_guide = db.relationship('StudyGuide')


class Inventory(db.Model):
    """
    This class creates the Inventory table in the database. The Inventory table contains the following columns:
    - id: The primary key of the table
    - user_id: The foreign key to the User table
    - study_guide_id: The foreign key to the StudyGuide table
    - study_guide: A relationship to the StudyGuide table
    - user: A relationship to the User table
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    study_guide_id = db.Column(db.Integer, db.ForeignKey('study_guide.id'), nullable=False)
    study_guide = db.relationship('StudyGuide')
    user = db.relationship('User', backref='inventory_items')
