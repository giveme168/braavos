# -*- coding: UTF-8 -*-
import datetime
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for, json

from . import db, BaseModelMixin

USER_STATUS_ON = 1         # 有效
USER_STATUS_OFF = 0        # 停用

USER_STATUS_CN = {
    USER_STATUS_OFF: u"停用",
    USER_STATUS_ON: u"有效"
}
TEAM_TYPE_SEARCH_AD_LEADER = 22  # 360搜索广告销售Leader
TEAM_TYPE_SEARCH_AD_SELLER = 21  # 360搜索广告销售
TEAM_TYPE_MEDIA_LEADER = 20       # 内部-媒介Leader
TEAM_TYPE_OPS_LEADER = 19  # 行政-Leader
TEAM_TYPE_OPS = 18  # 行政
TEAM_TYPE_HR_LEADER = 17  # 人力-Leader
TEAM_TYPE_HR = 16  # 人力
TEAM_TYPE_OPERATER_LEADER = 15       # 执行-Leader
TEAM_TYPE_SUPER_LEADER = 14       # Super-Leader
TEAM_TYPE_FINANCE = 13       # 内部-财务
TEAM_TYPE_MEDIA = 12       # 内部-媒介
TEAM_TYPE_DOUBAN_CONTRACT = 11       # 豆瓣-合同管理员
TEAM_TYPE_CONTRACT = 10       # 內部-合同管理员
TEAM_TYPE_LEADER = 9       # 内部-销售Leader
TEAM_TYPE_MEDIUM = 8       # 媒体
TEAM_TYPE_DESIGNER = 7       # 內部-设计
TEAM_TYPE_PLANNER = 6       # 內部-策划
TEAM_TYPE_OPERATER = 5     # 內部-執行
TEAM_TYPE_AGENT_SELLER = 4       # 內部-渠道銷售
TEAM_TYPE_DIRECT_SELLER = 3       # 內部-直客銷售
TEAM_TYPE_INAD = 2         # 内部-其他
TEAM_TYPE_ADMIN = 1        # 系统管理员
TEAM_TYPE_SUPER_ADMIN = 0  # 程序管理员

TEAM_TYPE_CN = {
    TEAM_TYPE_MEDIUM: u"媒体",
    TEAM_TYPE_DOUBAN_CONTRACT: u"豆瓣-合同",
    TEAM_TYPE_INAD: u"内部-其他",
    TEAM_TYPE_DESIGNER: u"内部-设计",
    TEAM_TYPE_PLANNER: u"内部-策划",
    TEAM_TYPE_OPERATER: u"内部-执行",
    TEAM_TYPE_DIRECT_SELLER: u"内部-销售",
    TEAM_TYPE_AGENT_SELLER: u'內部-渠道銷售',
    TEAM_TYPE_CONTRACT: u"内部-合同",
    TEAM_TYPE_MEDIA: u"内部-媒介",
    TEAM_TYPE_FINANCE: u"内部-财务",
    TEAM_TYPE_LEADER: u"内部-销售Leader",
    TEAM_TYPE_OPERATER_LEADER: u"内部-执行Leader",
    TEAM_TYPE_SUPER_LEADER: u"内部-SuperLeader",
    TEAM_TYPE_ADMIN: u" 系统管理员",
    TEAM_TYPE_SUPER_ADMIN: u"程序管理员",
    TEAM_TYPE_HR: u'内部人力',
    TEAM_TYPE_HR_LEADER: u'内部人力-Leader',
    TEAM_TYPE_OPS: u'内部行政',
    TEAM_TYPE_OPS_LEADER: u'内部行政-Leader',
    TEAM_TYPE_MEDIA_LEADER: u'内部-媒介Leader',
    TEAM_TYPE_SEARCH_AD_SELLER: u'360搜索广告销售',
    TEAM_TYPE_SEARCH_AD_LEADER: u'360搜索广告销售Leader'
}

TEAM_LOCATION_DEFAULT = 0
TEAM_LOCATION_HUABEI = 1
TEAM_LOCATION_HUADONG = 2
TEAM_LOCATION_HUANAN = 3
TEAM_LOCATION_ALL = 4
TEAM_LOCATION_CN = {
    TEAM_LOCATION_DEFAULT: u"其他",
    TEAM_LOCATION_HUABEI: u"华北",
    TEAM_LOCATION_HUADONG: u"华东",
    TEAM_LOCATION_HUANAN: u"华南",
    TEAM_LOCATION_ALL: u"全国",
}

DEFAULT_BIRTHDAY = datetime.date(year=1970, month=1, day=1)
DEFAULT_RECRUITED_DATE = datetime.date(year=1970, month=1, day=1)

team_leaders = db.Table('team_leaders',
                        db.Column(
                            'user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                        db.Column(
                            'leader_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
                        )


class User(db.Model, BaseModelMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    pwdhash = db.Column(db.String(100))
    status = db.Column(db.Integer)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    team = db.relationship('Team', backref=db.backref('users', lazy='dynamic'))
    team_leaders = db.relationship('User', secondary=team_leaders, primaryjoin=id == team_leaders.c.user_id,
                                   secondaryjoin=id == team_leaders.c.leader_id,
                                   backref="user_ids")
    birthday = db.Column(db.DateTime)
    recruited_date = db.Column(db.DateTime)

    def __init__(self, name, email, password, team, status=USER_STATUS_ON, team_leaders=[], birthday=None,
                 recruited_date=None):
        self.name = name
        self.email = email.lower()
        self.set_password(password)
        self.team = team
        self.status = status
        self.team_leaders = team_leaders
        self.birthday = birthday or DEFAULT_BIRTHDAY
        self.recruited_date = recruited_date or datetime.date.today()

    '''
    def __repr__(self):
        return '<User %s, %s>' % (self.name, self.email)
    '''

    # 是否是绩效考核leader
    @property
    def is_kpi_leader(self):
        return len([k for k in User.all() if self in k.team_leaders]) > 0

    def kpi_undering_users(self):
        return [k for k in User.all() if self in k.team_leaders]

    @property
    def display_name(self):
        return "%s@%s" % (self.name, self.team.name)

    @property
    def location(self):
        return self.team.location

    @property
    def location_cn(self):
        return self.team.location_cn

    @property
    def user_leaders(self):
        return self.team.admins or []

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
    def name_exist(cls, name):
        is_exist = User.query.filter_by(name=name).count() > 0
        return is_exist

    @property
    def avatar(self, size=48):
        return "http://gravatar.duoshuo.com/avatar/%s?s=%s&d=identicon" % (md5(self.email).hexdigest(), size)

    def is_super_admin(self):
        return self.team.is_super_admin()

    def is_admin(self):
        return self.team.is_admin()

    def is_super_leader(self):
        return self.is_admin() or self.team.type == TEAM_TYPE_SUPER_LEADER

    def is_leader(self):
        return self.is_admin() or self.team.type == TEAM_TYPE_LEADER or self.team.type == TEAM_TYPE_SUPER_LEADER or \
            self.team.type == TEAM_TYPE_SEARCH_AD_LEADER

    def is_operater_leader(self):
        return self.is_admin() or self.team.type == TEAM_TYPE_OPERATER_LEADER

    def is_OPS_leader(self):
        return self.is_admin() or self.team.type == TEAM_TYPE_OPS_LEADER

    def is_OPS(self):
        return self.is_admin() or self.team.type == TEAM_TYPE_OPS

    def is_HR_leader(self):
        return self.is_admin() or self.team.type == TEAM_TYPE_HR_LEADER

    def is_contract(self):
        return self.is_admin() or self.team.type == TEAM_TYPE_CONTRACT

    def is_operater(self):
        return self.is_admin() or self.team.type in [TEAM_TYPE_OPERATER, TEAM_TYPE_OPERATER_LEADER]

    def is_media(self):
        return self.is_admin() or self.team.type == TEAM_TYPE_MEDIA

    def is_media_leader(self):
        return self.is_admin() or self.team.type == TEAM_TYPE_MEDIA_LEADER

    def is_planner(self):
        return self.is_admin() or self.team.type == TEAM_TYPE_PLANNER

    def is_sale(self):
        return self.is_admin() or self.is_leader() or self.team.type == TEAM_TYPE_DIRECT_SELLER

    def is_finance(self):
        return self.is_admin() or self.team.type == TEAM_TYPE_FINANCE

    def path(self):
        return url_for('user.user_detail', user_id=self.id)

    def is_team_leader(self):
        admins = []
        for k in Team.all():
            admins += k.admins
        return self in admins

    def is_searchad_saler(self):
        return self.is_admin() or self.team.type == TEAM_TYPE_SEARCH_AD_SELLER

    def is_searchad_leader(self):
        return self.is_admin() or self.team.type == TEAM_TYPE_SEARCH_AD_LEADER

    def is_searchad_member(self):
        return self.is_searchad_saler() or self.is_searchad_leader() or self.is_super_leader()

    @classmethod
    def gets_by_team_type(cls, team_type):
        return [x for x in cls.all_active() if x.team.type == team_type]

    @classmethod
    def super_leaders(cls):
        return cls.gets_by_team_type(TEAM_TYPE_SUPER_LEADER)

    @classmethod
    def leaders(cls):
        return cls.gets_by_team_type(TEAM_TYPE_LEADER)

    @classmethod
    def HR_leaders(cls):
        return cls.gets_by_team_type(TEAM_TYPE_HR_LEADER)

    @classmethod
    def operater_leaders(cls):
        return cls.gets_by_team_type(TEAM_TYPE_OPERATER_LEADER)

    @classmethod
    def finances(cls):
        return cls.gets_by_team_type(TEAM_TYPE_FINANCE)

    @classmethod
    def sales(cls):
        return (cls.gets_by_team_type(TEAM_TYPE_DIRECT_SELLER) +
                cls.gets_by_team_type(TEAM_TYPE_AGENT_SELLER) +
                cls.leaders())

    @classmethod
    def searchAd_sales(cls):
        return (cls.gets_by_team_type(TEAM_TYPE_SEARCH_AD_SELLER) +
                cls.gets_by_team_type(TEAM_TYPE_SEARCH_AD_LEADER))

    @classmethod
    def contracts(cls):
        return cls.gets_by_team_type(TEAM_TYPE_CONTRACT)

    @classmethod
    def medias(cls):
        return cls.gets_by_team_type(TEAM_TYPE_MEDIA)

    @classmethod
    def douban_contracts(cls):
        return [x for x in cls.all() if x.team.type == TEAM_TYPE_DOUBAN_CONTRACT]

    @classmethod
    def admins(cls):
        return cls.gets_by_team_type(TEAM_TYPE_ADMIN)

    @classmethod
    def contracts_by_order(cls, order):
        return order.direct_sales + order.agent_sales + cls.contracts()

    @classmethod
    def douban_contracts_by_order(cls, order):
        return (cls.douban_contracts() + cls.contracts()
                + order.direct_sales + order.agent_sales
                + order.leaders + cls.medias())

    @classmethod
    def all_active(cls):
        return [u for u in cls.query.order_by(cls.id.desc()) if u.is_active()]

    @classmethod
    def outsource_leaders_email(cls, user, upper=False):
        leader_emails = [k for k in user.team.admins]
        operater_leaders = [
            k for k in cls.all() if k.team.type == TEAM_TYPE_OPERATER_LEADER and k.location == user.location]
        leader_emails += operater_leaders
        leader_emails += [k for k in cls.all()
                          if k.email.find('fenghaiyan') >= 0]
        if user.team.location in [TEAM_LOCATION_HUABEI, TEAM_LOCATION_HUADONG]:
            leader_emails += [k for k in cls.all() if k.email.find(
                'gaixin') >= 0 and k.team.type == TEAM_TYPE_SUPER_LEADER]
        else:
            leader_emails += [k for k in cls.all() if k.email.find(
                'huangliang') >= 0 and k.team.type == TEAM_TYPE_SUPER_LEADER]
        return leader_emails

    @classmethod
    def get_agent_user_by_location(cls, location):
        return [k for k in cls.all() if k.team.location == location
                and k.team.type in [TEAM_TYPE_AGENT_SELLER, TEAM_TYPE_LEADER]]

    @classmethod
    def get_direct_user_by_location(cls, location):
        return [k for k in cls.all() if k.team.location == location
                and k.team.type in [TEAM_TYPE_DIRECT_SELLER, TEAM_TYPE_LEADER]]

    @property
    def is_out_saler(self):
        return self.team.type in [TEAM_TYPE_AGENT_SELLER, TEAM_TYPE_DIRECT_SELLER, TEAM_TYPE_LEADER]

    @property
    def team_leaders_cn(self):
        return ','.join([k.name for k in self.team_leaders])

    @classmethod
    def get_all_today_is_birthday(cls):
        today = datetime.date.today()
        return [user for user in User.all() if user.birthday.month == today.month and user.birthday.day == today.day]

    @property
    def lately_commission(self):
        return self.commission_user.first()


team_admins = db.Table('team_admin_users',
                       db.Column(
                           'user_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column(
                           'team_id', db.Integer, db.ForeignKey('team.id'))
                       )


class Team(db.Model, BaseModelMixin):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.Integer)
    location = db.Column(db.Integer)
    admins = db.relationship('User', secondary=team_admins)

    def __init__(self, name, type=TEAM_TYPE_MEDIUM, location=TEAM_LOCATION_DEFAULT, admins=None):
        self.name = name
        self.type = type
        self.location = location
        self.admins = admins or []

    def __repr__(self):
        return '<Team %s, type=%s>' % (self.name, self.type_cn)

    @classmethod
    def name_exist(cls, name):
        is_exist = Team.query.filter_by(name=name).count() > 0
        return is_exist

    @property
    def type_cn(self):
        return TEAM_TYPE_CN[self.type]

    @property
    def location_cn(self):
        return TEAM_LOCATION_CN[self.location] if self.location else u"其他"

    def is_super_admin(self):
        return self.type == TEAM_TYPE_SUPER_ADMIN

    def is_admin(self):
        return self.is_super_admin() or self.type == TEAM_TYPE_ADMIN

    def is_medium(self):
        return self.type == TEAM_TYPE_MEDIUM


send_users = db.Table('leave_send_users',
                      db.Column(
                          'user_id', db.Integer, db.ForeignKey('user.id')),
                      db.Column(
                          'leave_id', db.Integer, db.ForeignKey('user_leave.id'))
                      )


LEAVE_TYPE_NORMAL = 1
LEAVE_TYPE_ANNUAL = 2
LEAVE_TYPE_SICK = 3
LEAVE_TYPE_MARRIAGE = 4
LEAVE_TYPE_MATERNITY = 5
LEAVE_TYPE_FUNERA = 6
LEAVE_TYPE_OFF = 7

LEAVE_TYPE_CN = {
    LEAVE_TYPE_NORMAL: u'事假',
    LEAVE_TYPE_ANNUAL: u'年假',
    LEAVE_TYPE_SICK: u'病假',
    LEAVE_TYPE_MARRIAGE: u'婚假',
    LEAVE_TYPE_MATERNITY: u'产假',
    LEAVE_TYPE_FUNERA: u'丧假',
    LEAVE_TYPE_OFF: u'调休'
}

LEAVE_STATUS_BACK = 0
LEAVE_STATUS_NORMAL = 1
LEAVE_STATUS_APPLY = 2
LEAVE_STATUS_PASS = 3
LEAVE_STATUS_APPLYBACK = 4

LEAVE_STATUS_CN = {
    LEAVE_STATUS_BACK: u'撤销申请',
    LEAVE_STATUS_NORMAL: u'待申请',
    LEAVE_STATUS_APPLY: u'申请中',
    LEAVE_STATUS_PASS: u'通过申请',
    LEAVE_STATUS_APPLYBACK: u'不通过',
}


class Leave(db.Model, BaseModelMixin):
    __tablename__ = 'user_leave'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    rate_day = db.Column(db.String(20))
    reason = db.Column(db.String(100))
    status = db.Column(db.Integer)
    senders = db.relationship('User', secondary=send_users)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(
        'User', backref=db.backref('creator_leave', lazy='dynamic'))
    create_time = db.Column(db.DateTime)
    __mapper_args__ = {'order_by': id.desc()}

    def __init__(self, type, start_time=None, end_time=None, rate_day='0-1', reason='',
                 senders=None, creator=None, create_time=None, status=1):
        self.type = type
        self.start_time = start_time or datetime.date.today()
        self.end_time = end_time or datetime.date.today()
        self.reason = reason
        self.senders = senders or []
        self.creator = creator
        self.status = status
        self.create_time = datetime.date.today()
        self.rate_day = rate_day

    @property
    def type_cn(self):
        return LEAVE_TYPE_CN[self.type]

    @property
    def status_cn(self):
        return LEAVE_STATUS_CN[self.status]

    @property
    def start_time_cn(self):
        return self.start_time.strftime('%Y-%m-%d %H')

    @property
    def end_time_cn(self):
        return self.end_time.strftime('%Y-%m-%d %H')

    @property
    def create_time_cn(self):
        return self.create_time.strftime('%Y-%m-%d')

    def is_long_leave(self):
        date = self.rate_day.split('-')
        if int(date[0]) >= 5:
            return True
        else:
            return False

    @property
    def rate_day_cn(self):
        date = self.rate_day.split('-')
        if int(date[1]) == 0:
            return str(date[0]) + u'天整'
        elif int(date[1]) == 1:
            return str(date[0]) + u'天+上半天'
        elif int(date[1]) == 2:
            return str(date[0]) + u'天+下半天'
        else:
            return ''

    @property
    def leave_time_cn(self):
        offset = (self.end_time - self.start_time)
        hours = offset.seconds / 60 / 60
        if offset.days > 0:
            if 9 > hours > 0:
                return str(offset.days) + u'天半'
            elif hours == 9:
                return str(offset.days + 1) + u'天'
            else:
                return str(offset.days) + u'天'
        else:
            if 9 > hours > 0:
                return str(offset.days) + u'天半'
            elif hours == 9:
                return u'1天'
            else:
                return u'0天'


OUT_CREATOR_TYPE_SALER = 1
OUT_CREATOR_TYPE_NORMAL = 2
OUT_CREATOR_TYPE_CN = {
    OUT_CREATOR_TYPE_SALER: u'销售',
    OUT_CREATOR_TYPE_NORMAL: u'普通'
}

OUT_STATUS_NEW = 0
OUT_STATUS_APPLY = 1
OUT_STATUS_PASS = 2
OUT_STATUS_MEETED = 3
OUT_STATUS_MEETED_NOT_PASS = 4
OUT_STATUS_CN = {
    OUT_STATUS_NEW: u'新添加',
    OUT_STATUS_APPLY: u'外出报备申请中',
    OUT_STATUS_PASS: u'外出报备申请通过',
    OUT_STATUS_MEETED: u'会议纪要填写完毕',
    OUT_STATUS_MEETED_NOT_PASS: u'未审批-会议纪要填写完毕',
}

OUT_M_PERSION_TYPE_NORMAL = 1
OUT_M_PERSION_TYPE_OTHER = 2


out_joiners = db.Table('out_joiners',
                       db.Column(
                           'user_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column(
                           'out_id', db.Integer, db.ForeignKey('user_out.id'))
                       )


class Out(db.Model, BaseModelMixin):
    __tablename__ = 'user_out'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    address = db.Column(db.String(300))
    reason = db.Column(db.Text())             # 外出原因
    meeting_s = db.Column(db.Text())          # 会议纪要
    persions = db.Column(db.String(300))      # 会见人
    m_persion = db.Column(db.String(200))     # 公司名称
    m_persion_type = db.Column(db.Integer)    # 公司名称类型
    creator_type = db.Column(db.Integer)      # 创建人类型：销售 or 普通
    status = db.Column(db.Integer)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(
        'User', backref=db.backref('creator_out', lazy='dynamic'))
    create_time = db.Column(db.DateTime)
    joiners = db.relationship('User', secondary=out_joiners)
    __mapper_args__ = {'order_by': id.desc()}

    def __init__(self, start_time, end_time, reason, m_persion, creator, m_persion_type,
                 address, persions, meeting_s='', creator_type=1, status=1,
                 joiners=None, create_time=None):
        self.start_time = start_time
        self.end_time = end_time
        self.address = address
        self.persions = persions
        self.reason = reason
        self.meeting_s = meeting_s
        self.m_persion = m_persion
        self.m_persion_type = m_persion_type
        self.creator_type = creator_type
        self.status = status
        self.creator = creator
        self.joiners = joiners or []
        self.create_time = create_time or datetime.date.today()

    @property
    def start_time_cn(self):
        return self.start_time.strftime('%Y-%m-%d %H:%M')

    @property
    def end_time_cn(self):
        return self.end_time.strftime('%Y-%m-%d %H:%M')

    @property
    def status_cn(self):
        return OUT_STATUS_CN[self.status]

    @property
    def m_persion_cn(self):
        if self.m_persion_type == 1:
            m_persion_p = self.m_persion.split('-')
            return m_persion_p[2]
        else:
            return self.m_persion

    @property
    def is_meeting(self):
        return int(self.create_time.strftime('%Y%m%d')) < int(datetime.datetime.now().strftime('%Y%m%d'))


P_VERSION_ITEMS = [{'type': 1, 'name': u'2015上半年'}]
P_VERSION_CN = {
    1: u'2015年上半年'
}

P_TYPE_CN = {
    1: u'普通员工表',
    2: u'管理人员表'
}

P_STATUS_NEW = 1
P_STATUS_APPLY = 2
P_STATUS_APPLY_END = 3
P_STATUS_HR = 4
P_STATUS_END = 5
P_STATUS_CN = {
    P_STATUS_NEW: u'新添加',
    P_STATUS_APPLY: u'领导评分中',
    P_STATUS_APPLY_END: u'领导评分完成',
    P_STATUS_HR: u'HR整理中',
    P_STATUS_END: u'归档',
}


class PerformanceEvaluation(db.Model, BaseModelMixin):
    __tablename__ = 'user_preformance_evaluation'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer)  # 表格类型: 1 普通员工表; 2 管理人员表
    version = db.Column(db.Integer, default=1)  # 表格版本
    status = db.Column(db.Integer, default=1)  # 状态

    upper_score = db.Column(db.Float, default=0.0)
    self_upper_score = db.Column(db.Float, default=0.0)
    KR_score = db.Column(db.Float, default=0.0)
    self_KR_score = db.Column(db.Float, default=0.0)
    manage_score = db.Column(db.Float, default=0.0)
    self_manage_score = db.Column(db.Float, default=0.0)
    ability_score = db.Column(db.Float, default=0.0)
    self_ability_score = db.Column(db.Float, default=0.0)
    partner_score = db.Column(db.Float, default=0.0)
    total_score = db.Column(db.Float, default=0.0)
    self_total_score = db.Column(db.Float, default=0.0)

    now_report = db.Column(db.Text())
    future_report = db.Column(db.Text())
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(
        'User', backref=db.backref('creator_performance_evaluation', lazy='dynamic'))
    create_time = db.Column(db.DateTime)
    body = db.Column(db.Text(), default=json.dumps({}))
    __mapper_args__ = {'order_by': id.desc()}

    def __init__(self, now_report, future_report, creator, upper_score=0.00,
                 KR_score=0.00, manage_score=0.00, ability_score=0.00, total_score=0.00,
                 self_upper_score=0.00, self_KR_score=0.00, self_manage_score=0.00,
                 self_ability_score=0.00, self_total_score=0.00, partner_score=0.00,
                 type=1, status=1, version=1, create_time=None):
        self.type = type
        self.version = version or 1
        self.status = status
        self.upper_score = upper_score
        self.KR_score = KR_score
        self.manage_score = manage_score
        self.ability_score = ability_score
        self.partner_score = partner_score
        self.total_score = total_score
        self.self_upper_score = self_upper_score
        self.self_KR_score = self_KR_score
        self.self_manage_score = self_manage_score
        self.self_ability_score = self_ability_score
        self.self_total_score = self_total_score
        self.now_report = now_report
        self.future_report = future_report
        self.creator = creator
        self.create_time = create_time or datetime.datetime.now()

    @property
    def type_cn(self):
        return P_TYPE_CN[self.type]

    @property
    def version_cn(self):
        return P_VERSION_CN[self.version]

    @property
    def status_cn(self):
        return P_STATUS_CN[self.status]

    @property
    def create_time_cn(self):
        return self.create_time.strftime('%Y-%m-%d')
