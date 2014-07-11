#-*- coding: UTF-8 -*-
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, BaseModelMixin

USER_STATUS_ON = 1         # 有效
USER_STATUS_OFF = 0        # 停用

USER_STATUS_CN = {
    USER_STATUS_OFF: u"停用",
    USER_STATUS_ON: u"有效"
}

TEAM_TYPE_MEDIUM = 5       # 媒体
TEAM_TYPE_OPERATER = 4     # 內部-執行
TEAM_TYPE_SELLER = 3       # 內部-銷售
TEAM_TYPE_INAD = 2         # 内部-其他
TEAM_TYPE_ADMIN = 1        # 管理员
TEAM_TYPE_SUPER_ADMIN = 0  # 超级管理员

TEAM_TYPE_CN = {
    TEAM_TYPE_OPERATER: u"内部-执行",
    TEAM_TYPE_SELLER: u"内部-销售",
    TEAM_TYPE_MEDIUM: u"媒体",
    TEAM_TYPE_INAD: u"内部-其他",
    TEAM_TYPE_ADMIN: u" 广告管理员",
    TEAM_TYPE_SUPER_ADMIN: u"系统管理员"
}


class User(db.Model, BaseModelMixin):
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

    def get_id(self):
        return self.id

    def is_anonymous(self):
        return False

    def is_active(self):
        return self.status == USER_STATUS_ON

    def is_authenticated(self):
        return self.is_active()

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()


class Team(db.Model, BaseModelMixin):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.Integer)

    def __init__(self, name, type=TEAM_TYPE_MEDIUM):
        self.name = name.title()
        self.type = type

    def __repr__(self):
        return '<Team %s>' % (self.name)

    @property
    def type_cn(self):
        return TEAM_TYPE_CN[self.type]

    def is_super_admin(self):
        return self.type == TEAM_TYPE_SUPER_ADMIN

    def is_admin(self):
        return self.is_super_admin() or self.type == TEAM_TYPE_ADMIN
