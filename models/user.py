from werkzeug.security import generate_password_hash, check_password_hash
from libs.db import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    pwdhash = db.Column(db.String(100))

    def __init__(self, name, email, password):
        self.name = name.title()
        self.email = email.lower()
        self.set_password(password)

    def __repr__(self):
        return '<User %s, %s>' % (self.name, self.email)

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)
        db.session.commit()

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

    def add(self):
        if not User.query.filter_by(email=self.email).first():
            db.session.add(self)
            db.session.commit()
