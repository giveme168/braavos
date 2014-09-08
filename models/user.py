# -*- coding: UTF-8 -*-
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for

from . import db, BaseModelMixin

USER_STATUS_ON = 1         # 有效
USER_STATUS_OFF = 0        # 停用

USER_STATUS_CN = {
    USER_STATUS_OFF: u"停用",
    USER_STATUS_ON: u"有效"
}

TEAM_TYPE_LEADER = 9       # 媒体
TEAM_TYPE_MEDIUM = 8       # 媒体
TEAM_TYPE_DESIGNER = 7       # 內部-设计
TEAM_TYPE_PLANNER = 6       # 內部-策划
TEAM_TYPE_OPERATER = 5     # 內部-執行
TEAM_TYPE_AGENT_SELLER = 4       # 內部-渠道銷售
TEAM_TYPE_DIRECT_SELLER = 3       # 內部-直客銷售
TEAM_TYPE_INAD = 2         # 内部-其他
TEAM_TYPE_ADMIN = 1        # 管理员
TEAM_TYPE_SUPER_ADMIN = 0  # 超级管理员

TEAM_TYPE_CN = {
    TEAM_TYPE_MEDIUM: u"媒体",
    TEAM_TYPE_DESIGNER: u"内部-设计",
    TEAM_TYPE_PLANNER: u"内部-策划",
    TEAM_TYPE_OPERATER: u"内部-执行",
    TEAM_TYPE_AGENT_SELLER: u"内部-渠道销售",
    TEAM_TYPE_DIRECT_SELLER: u"内部-直客销售",
    TEAM_TYPE_INAD: u"内部-其他",
    TEAM_TYPE_LEADER: u"内部-Leader",
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
        self.name = name
        self.email = email.lower()
        self.set_password(password)
        self.phone = phone
        self.team = team
        self.status = status

    def __repr__(self):
        return '<User %s, %s>' % (self.name, self.email)

    @property
    def display_name(self):
        return "%s@%s" % (self.name, self.team.name)

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)
        self.save()

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

    @classmethod
    def gets_by_team_type(cls, team_type):
        return [x for x in cls.all() if x.team.type == team_type]

    @property
    def avatar(self, size=48):
        return "http://www.gravatar.com/avatar/%s?s=%s&d=identicon" % (md5(self.email).hexdigest(), size)

    def is_admin(self):
        return self.team.is_admin()

    def is_leader(self):
        return self.team.type == TEAM_TYPE_LEADER

    def path(self):
        return url_for('user.user_detail', user_id=self.id)


class Team(db.Model, BaseModelMixin):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.Integer)

    def __init__(self, name, type=TEAM_TYPE_MEDIUM):
        self.name = name
        self.type = type

    def __repr__(self):
        return '<Team %s, type=%s>' % (self.name, self.type_cn)

    @property
    def type_cn(self):
        return TEAM_TYPE_CN[self.type]

    def is_super_admin(self):
        return self.type == TEAM_TYPE_SUPER_ADMIN

    def is_admin(self):
        return self.is_super_admin() or self.type == TEAM_TYPE_ADMIN

    def is_medium(self):
        return self.type == TEAM_TYPE_MEDIUM
