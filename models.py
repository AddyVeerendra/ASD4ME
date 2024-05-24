from extensions import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    wallet = db.Column(db.Integer, nullable=False, default=0)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

class StudyGuide(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    Class = db.Column(db.String(20), nullable=False)
    UnitTopic = db.Column(db.String(20), nullable=False)
    Price = db.Column(db.Integer, nullable=False)
    Creator = db.Column(db.String(20), nullable=False)
    Link = db.Column(db.String(100), nullable=False)

class PendingStudyGuide(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    Class = db.Column(db.String(20), nullable=False)
    UnitTopic = db.Column(db.String(20), nullable=False)
    Price = db.Column(db.Integer, nullable=False)
    Creator = db.Column(db.String(20), nullable=False)
    Link = db.Column(db.String(100), nullable=False)