from src import db
from sqlalchemy import ForeignKey

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String, unique = True, nullable = False)
    password = db.Column(db.String, nullable = False)
    filename = db.Column(db.String, nullable = True)

    subjects = db.relationship('Subject', back_populates='user')
    reports = db.relationship('Report', back_populates = 'user')


class Subject(db.Model):
    section = db.Column(db.Integer, primary_key = True)
    id = db.Column(db.String, nullable = False)
    unit = db.Column(db.Float, nullable = False)
    name = db.Column(db.String, nullable = False)
    grade = db.Column(db.Float, nullable = False)
    user_id = db.Column(db.Integer, ForeignKey('user.id'))

    user = db.relationship('User', back_populates='subjects')

class Report(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    category = db.Column(db.String, nullable = False)
    report= db.Column(db.String(500), nullable = False)
    user_id = db.Column(db.Integer, ForeignKey('user.id'))


    user = db.relationship('User', back_populates='reports')