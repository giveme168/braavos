#-*- coding: UTF-8 -*-
from werkzeug.security import generate_password_hash, check_password_hash
from libs.db import db

USER_STATUS_ON = 1         # 有效
USER_STATUS_OFF = 0        # 停用

TEAM_TYPE_MEDIUM = 3       # 媒体
TEAM_TYPE_INAD = 2         # inad内部team
TEAM_TYPE_ADMIN = 1        # 管理员
TEAM_TYPE_SUPER_ADMIN = 0  # 超级管理员


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    pwdhash = db.Column(db.String(100))
    phone = db.Column(db.String(120), unique=True)
    status = db.Column(db.Integer)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    team = db.relationship('Team', backref=db.backref('users', lazy='dynamic'))

    def __init__(self, name, email, password, phone, team, status=USER_STATUS_ON):
        self.name = name.title()
        self.email = email.lower()
        self.set_password(password)
        self.phone = phone
        self.team = team
        self.status = status

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

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Team(db.Model):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.Integer)

    def __init__(self, name, type=TEAM_TYPE_MEDIUM):
        self.name = name.title()
        self.type = type

    def __repr__(self):
        return '<Team %s>' % (self.name)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
