# -*- coding: utf-8 -*-
import datetime

from . import db, BaseModelMixin
from user import User
from models.mixin.comment import CommentMixin

BREF_STATUS_CLOSE = 0
BREF_STATUS_NEWS = 1
BREF_STATUS_APPLY = 2
BREF_STATUS_FOLLOW = 3
BREF_STATUS_CANNCEL = 10

BREF_STATUS_CN = {
    BREF_STATUS_CLOSE: u'完成',
    BREF_STATUS_NEWS: u'新建',
    BREF_STATUS_APPLY: u'申请中',
    BREF_STATUS_FOLLOW: u'已分配',
    BREF_STATUS_CANNCEL: u'取消'
}

BUDGET_TYPE_50 = 1
BUDGET_TYPE_100 = 2
BUDGET_TYPE_150 = 3
BUDGET_TYPE_200 = 4
BUDGET_TYPE_500 = 5
BUDGET_TYPE_UP = 6

BUDGET_TYPE_CN = {
    BUDGET_TYPE_50: u'0-50W',
    BUDGET_TYPE_100: u'50-100W',
    BUDGET_TYPE_150: u'100-150W',
    BUDGET_TYPE_200: u'150-200W',
    BUDGET_TYPE_500: u'200-500W',
    BUDGET_TYPE_UP: u'500W以上',
}

IS_TEMP_FALSE = 0
IS_TEMP_TRUE = 1

IS_TEMP_CN = {
    IS_TEMP_FALSE: u'无模板',
    IS_TEMP_TRUE: u'有模板'
}

AGENT_YTPE_DIRECT = 1
AGENT_YTPE_AGENT = 2
AGENT_YTPE_CN = {
    AGENT_YTPE_DIRECT: u'直客需求',
    AGENT_YTPE_AGENT: u'代理需求'
}

USE_TYPE_READ = 1
USE_TYPE_TALK = 2
USE_TYPE_GOOD = 3
USE_TYPE_EXECUTE = 4

USE_TYPE_CN = {
    USE_TYPE_READ: u'阅读版',
    USE_TYPE_TALK: u'演讲版',
    USE_TYPE_GOOD: u'干货版',
    USE_TYPE_EXECUTE: u'执行版',
}

LEVEL_TYPE_NOMRAL = 1
LEVEL_TYPE_GENERAL = 2
LEVEL_TYPE_COMPLEX = 3

LEVEL_TYPE_CN = {
    LEVEL_TYPE_NOMRAL: u'C级：简单资源推荐、word版本等——至少1天',
    LEVEL_TYPE_GENERAL: u'B级：普通策略案、创意案、细化执行案——至少2天',
    LEVEL_TYPE_COMPLEX: u'A级：复杂策略案、百万级大案、全年案、培训稿等——至少3天',
}


# 策划案例
class Bref(db.Model, BaseModelMixin, CommentMixin):
    __tablename__ = 'bra_planning_bref'
    id = db.Column(db.Integer, primary_key=True)
    #  基本信息
    title = db.Column(db.String(200))
    agent = db.Column(db.String(200))
    brand = db.Column(db.String(100))  # 品牌
    product = db.Column(db.String(100))  # 产品
    target = db.Column(db.String(200))  # 目标受众
    background = db.Column(db.String(250))  # 背景
    push_target = db.Column(db.String(250))  # 推广目的
    push_theme = db.Column(db.String(250))  # 推广主题
    push_time = db.Column(db.String(250))   # 推广周期
    budget = db.Column(db.Integer, default=1)  # 推广预算
    is_temp = db.Column(db.Integer, default=0)  # 有无模板

    # 项目信息
    agent_type = db.Column(db.Integer, default=1)  # 下单需求方
    use_type = db.Column(db.Integer, default=1)    # 应用场景
    level = db.Column(db.Integer, default=1)   # 项目等级
    get_time = db.Column(db.DateTime)   # 提交时间

    # 补充说明
    intent_medium = db.Column(db.String(100))   # 品牌意向媒体
    suggest = db.Column(db.String(200))     # 建议
    desc = db.Column(db.Text())   # 备注

    url = db.Column(db.String(300))  # 网盘链接
    status = db.Column(db.Integer, default=1)
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(
        'User', backref=db.backref('bref_user', lazy='dynamic'))
    follow_id = db.Column(db.Integer, default=0)  # 分配人
    to_id = db.Column(db.Integer, default=0)   # 指派给
    cc = db.Column(db.Text())
    __mapper_args__ = {'order_by': id.desc()}

    def __init__(self, title, agent, brand, product, target, background, push_target,
                 push_theme, push_time, budget, is_temp, agent_type, use_type, level,
                 get_time, intent_medium, suggest, desc, creator, status, follow_id,
                 to_id, url=None, create_time=None, update_time=None, cc=''):
        self.title = title
        self.agent = agent
        self.status = status
        self.brand = brand
        self.product = product
        self.target = target
        self.background = background
        self.push_target = push_target
        self.push_theme = push_theme
        self.push_time = push_time
        self.is_temp = is_temp
        self.agent_type = agent_type
        self.use_type = use_type
        self.budget = budget
        self.level = level
        self.intent_medium = intent_medium
        self.suggest = suggest
        self.url = url or ''
        self.creator = creator
        self.desc = desc
        self.follow_id = follow_id
        self.to_id = to_id
        self.get_time = get_time or datetime.datetime.now()
        self.create_time = create_time or datetime.datetime.now()
        self.update_time = update_time or datetime.datetime.now()
        self.cc = cc or ''

    @property
    def follower(self):
        if self.follow_id != 0:
            return User.get(self.follow_id)
        return None

    @property
    def toer(self):
        if self.to_id != 0:
            return User.get(self.to_id)
        return None

    @property
    def status_cn(self):
        return BREF_STATUS_CN[self.status]

    @property
    def create_time_cn(self):
        return self.create_time.strftime('%Y-%m-%d %H')

    @property
    def update_time_cn(self):
        return self.update_time.strftime('%Y-%m-%d %H')

    @property
    def get_time_cn(self):
        return self.get_time.strftime('%Y-%m-%d %H')

    @property
    def budget_cn(self):
        return BUDGET_TYPE_CN[self.budget]

    @property
    def is_temp_cn(self):
        return IS_TEMP_CN[self.is_temp]

    @property
    def agent_type_cn(self):
        return AGENT_YTPE_CN[self.agent_type]

    @property
    def use_type_cn(self):
        return USE_TYPE_CN[self.use_type]

    @property
    def level_cn(self):
        return LEVEL_TYPE_CN[self.level]

    @property
    def info(self):
        return '%s%s%s' % (self.title, self.brand, self.product)

    @property
    def url_cn(self):
        return self.url or u'未完成'

    # 策划单紧急状况
    @property
    def level_status(self):
        if (self.get_time - self.create_time).days < self.level:
            return 1
        return 0

    @property
    def name(self):
        return self.title

    @property
    def location(self):
        if self.creator.location == 4:
            location = 1
        else:
            location = self.creator.location
        return location
