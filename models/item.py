# -*- coding: utf-8 -*-
import datetime
from flask import url_for

from . import db, BaseModelMixin
from models.mixin.comment import CommentMixin
from models.mixin.delivery import DeliveryMixin
from consts import STATUS_CN, STATUS_ON, DATE_FORMAT, STATUS_OFF

SALE_TYPE_NORMAL = 0         # 标准, 购买
SALE_TYPE_GIFT = 1           # 配送
SALE_TYPE_REMNANT = 2         # 补量
# SALE_TYPE_CPC = 3            # CPC

SALE_TYPE_CN = {
    SALE_TYPE_NORMAL: u"购买",
    SALE_TYPE_GIFT: u"配送",
    SALE_TYPE_REMNANT: u"补量",
    # SALE_TYPE_CPC: u"CPC",
}

AD_TYPE_NORMAL = 0
AD_TYPE_CPD = 1
AD_TYPE_REMNANT = 2

AD_TYPE_CN = {
    AD_TYPE_NORMAL: u"CPM",
    AD_TYPE_CPD: u"CPD",
    AD_TYPE_REMNANT: u"补余",
}

PRIORITY_MID = 0
PRIORITY_HIG = 1
PRIORITY_LOW = 2

PRIORITY_CN = {
    PRIORITY_MID: u"普通",
    PRIORITY_HIG: u"高",
    PRIORITY_LOW: u"低",
}

SPEED_NORMAL = 0
SPEED_ASAP = 1

SPEED_CN = {
    SPEED_NORMAL: u"均匀",
    SPEED_ASAP: u"越快越好"
}

ITEM_STATUS_NEW = 0
ITEM_STATUS_PRE = 1
ITEM_STATUS_PRE_PASS = 2
ITEM_STATUS_ORDER_APPLY = 3
ITEM_STATUS_ORDER = 4

OCCUPY_RESOURCE_STATUS = [
    ITEM_STATUS_PRE,
    ITEM_STATUS_PRE_PASS,
    ITEM_STATUS_ORDER_APPLY,
    ITEM_STATUS_ORDER
]

PER_ORDER_ITEM_STATUS = [
    ITEM_STATUS_PRE,
    ITEM_STATUS_PRE_PASS,
    ITEM_STATUS_ORDER_APPLY
]

ITEM_STATUS_CN = {
    ITEM_STATUS_NEW: u"未下单",
    ITEM_STATUS_PRE: u"预下单(待审核)",
    ITEM_STATUS_PRE_PASS: u"预下单(通过)",
    ITEM_STATUS_ORDER_APPLY: u"下单(待审核)",
    ITEM_STATUS_ORDER: u"已下单"
}

ITEM_STATUS_ACTION_PRE_ORDER = 0
ITEM_STATUS_ACTION_PRE_ORDER_PASS = 1
ITEM_STATUS_ACTION_PRE_ORDER_REJECT = 2
ITEM_STATUS_ACTION_ORDER_APPLY = 3
ITEM_STATUS_ACTION_ORDER_PASS = 4
ITEM_STATUS_ACTION_ORDER_REJECT = 5
ITEM_STATUS_ACTION_ACTIVE = 6
ITEM_STATUS_ACTION_PAUSE = 7

ITEM_STATUS_LEADER_ACTIONS = [
    ITEM_STATUS_ACTION_PRE_ORDER_PASS,
    ITEM_STATUS_ACTION_PRE_ORDER_REJECT,
    ITEM_STATUS_ACTION_ORDER_PASS,
    ITEM_STATUS_ACTION_ORDER_REJECT
]

ITEM_STATUS_AGREE_ACTION = [
    ITEM_STATUS_ACTION_PRE_ORDER_PASS,
    ITEM_STATUS_ACTION_ORDER_PASS
]

ITEM_STATUS_ACTION_CN = {
    ITEM_STATUS_ACTION_PRE_ORDER: u"预下单",
    ITEM_STATUS_ACTION_PRE_ORDER_PASS: u"通过(预下单)",
    ITEM_STATUS_ACTION_PRE_ORDER_REJECT: u"不通过(预下单)",
    ITEM_STATUS_ACTION_ORDER_APPLY: u"申请下单",
    ITEM_STATUS_ACTION_ORDER_PASS: u"通过(下单)",
    ITEM_STATUS_ACTION_ORDER_REJECT: u"不通过(下单)",
    ITEM_STATUS_ACTION_ACTIVE: u"开启",
    ITEM_STATUS_ACTION_PAUSE: u"暂停",
}

ITEM_ACTION_CN = {
    ITEM_STATUS_ACTION_PRE_ORDER: u"预下单",
    ITEM_STATUS_ACTION_ORDER_APPLY: u"下单",
    ITEM_STATUS_ACTION_PRE_ORDER_PASS: u"预下单通过",
    ITEM_STATUS_ACTION_PRE_ORDER_REJECT: u"预下单不通过",
    ITEM_STATUS_ACTION_ORDER_PASS: u"下单通过",
    ITEM_STATUS_ACTION_ORDER_REJECT: u"下单不通过"
}

ORDER_REJECT = (ITEM_STATUS_ACTION_PRE_ORDER_REJECT, ITEM_STATUS_ACTION_ORDER_REJECT)


class AdItem(db.Model, BaseModelMixin, CommentMixin, DeliveryMixin):
    __tablename__ = 'bra_item'
    # 基础
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('bra_order.id'))
    order = db.relationship('Order', backref=db.backref('items', lazy='dynamic'))
    description = db.Column(db.String(500))
    # 排期
    sale_type = db.Column(db.Integer)  # 售卖类型: 购买, 配送, 补量, CPC
    position_id = db.Column(db.Integer, db.ForeignKey('ad_position.id'))
    position = db.relationship('AdPosition', backref=db.backref('order_items', lazy='dynamic'))
    special_sale = db.Column(db.Boolean)  # 特殊投放
    price = db.Column(db.Integer)
    # 投放
    ad_type = db.Column(db.Integer, default=0)  # 广告类型: 标准, CPD, 补余
    priority = db.Column(db.Integer, default=0)  # 优先级
    speed = db.Column(db.Integer, default=0)  # 投放速度
    status = db.Column(db.Integer, default=1)  # 状态: 暂停, 投放
    item_status = db.Column(db.Integer, default=0)  # 状态: 预下单, 下单
    # 创建者
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref=db.backref('created_items', lazy='dynamic'))
    create_time = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self, order, sale_type, special_sale, position, creator, create_time):
        self.order = order
        self.sale_type = sale_type
        self.special_sale = special_sale
        self.position = position
        self.creator = creator
        self.create_time = create_time

    def __repr__(self):
        return '<AdItem %s>' % (self.name)

    @property
    def name(self):
        return "%s-%s" % (self.position.name, self.description or u"描述")

    def is_online_ready(self):
        """是否可以开始投放, 供导出数据的时候使用"""
        return all([self.status == STATUS_ON,
                    self.item_status == ITEM_STATUS_ORDER,
                    self.materials.count() > 0])

    def is_online_by_date(self, _date):
        """是否正在投放"""
        return self.is_online_ready() and self.schedule_by_date(_date)

    def is_online_now(self):
        """当前是否正在投放"""
        return self.is_online_by_date(datetime.date.today())

    # used in the templates
    def is_status_on(self):
        return self.status == STATUS_ON

    @property
    def sale_type_cn(self):
        return SALE_TYPE_CN[self.sale_type]

    @property
    def status_cn(self):
        return STATUS_CN[self.status]

    @property
    def item_state_cn(self):
        return ITEM_STATUS_CN[self.item_status]

    @property
    def start_date(self):
        return min([s.date for s in self.schedules]) if self.schedules else None

    @property
    def start_date_cn(self):
        return self.start_date.strftime(DATE_FORMAT) if self.start_date else u"起始时间"

    @property
    def end_date(self):
        return max([s.date for s in self.schedules]) if self.schedules else None

    @property
    def end_date_cn(self):
        return self.end_date.strftime(DATE_FORMAT) if self.end_date else u"起始时间"

    def schedule_by_date(self, _date):
        schedules = [s for s in self.schedules if s.date == _date]
        return schedules[0] if schedules else None

    def schedule_sum_by_date(self, _date):
        schedules_num = [s.num for s in self.schedules if s.date == _date]
        return sum(schedules_num) if schedules_num else 0

    @property
    def schedule_sum(self):
        return sum([x.num for x in self.schedules])

    def get_schedule_info_by_week(self):
        ret = {}
        for x in range((self.end_date - self.start_date).days + 1):
            _date = self.start_date + datetime.timedelta(days=x)
            schedule = self.schedule_by_date(_date)
            info_dict = {}
            info_dict['date'] = _date
            info_dict['schedule'] = schedule
            info_dict['num'] = schedule.num if schedule else 0
            info_dict['can_order_num'] = self.position.can_order_num(_date)
            week = _date.isocalendar()[1]
            weekday = _date.isoweekday()
            week_info = ret.get(week, {})
            week_info[weekday] = info_dict
            ret[week] = week_info
        return ret

    @property
    def is_schedule_lock(self):
        return self.item_status != ITEM_STATUS_NEW

    @classmethod
    def update_items_with_action(cls, items, action, user):
        next_status = ITEM_STATUS_PRE
        status = STATUS_ON

        if action == ITEM_STATUS_ACTION_PRE_ORDER:
            next_status = ITEM_STATUS_PRE
        elif action == ITEM_STATUS_ACTION_PRE_ORDER_PASS:
            next_status = ITEM_STATUS_PRE_PASS
        elif action == ITEM_STATUS_ACTION_PRE_ORDER_REJECT:
            next_status = ITEM_STATUS_NEW
        elif action == ITEM_STATUS_ACTION_ORDER_APPLY:
            next_status = ITEM_STATUS_ORDER_APPLY
        elif action == ITEM_STATUS_ACTION_ORDER_PASS:
            next_status = ITEM_STATUS_ORDER
        elif action == ITEM_STATUS_ACTION_ORDER_REJECT:
            next_status = ITEM_STATUS_PRE_PASS
        elif action == ITEM_STATUS_ACTION_ACTIVE:
            status = STATUS_ON
        elif action == ITEM_STATUS_ACTION_PAUSE:
            status = STATUS_OFF

        # update the item_status or the status based on the action
        for i in items:
            if action in [ITEM_STATUS_ACTION_ACTIVE, ITEM_STATUS_ACTION_PAUSE]:
                i.status = status
            else:
                i.item_status = next_status
            i.save()
            i.add_comment(user, "%s : %s " % (i.name, ITEM_STATUS_ACTION_CN[action]))

    def path(self):
        return url_for('order.item_detail', item_id=self.id)

    @classmethod
    def get_next_step(self, step, action):
        if action in ORDER_REJECT:
            step = int(step) - 1
        else:
            step = int(step) + 1
        return step


class AdSchedule(db.Model, BaseModelMixin):
    __tablename__ = 'bra_schedule'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('bra_item.id'))
    item = db.relationship('AdItem', backref=db.backref('schedules', lazy='dynamic'))
    num = db.Column(db.Integer)  # 投放量
    date = db.Column(db.Date)  # 投放日期
    start = db.Column(db.Time)  # 开始时间
    end = db.Column(db.Time)  # 结束时间

    def __init__(self, item, num, date, start=datetime.time.min, end=datetime.time.max):
        self.item = item
        self.num = num
        self.date = date
        self.start = start
        self.end = end

    def __repr__(self):
        return '<AdSchedule %s-%s>' % (self.item.name, self.date)

    @property
    def units(self):
        return self.item.position.units

    @classmethod
    def export_schedules(cls, _date):
        return [s for s in cls.all() if s.date == _date and s.item.is_online_by_date(_date)]


class ChangeStateApply(object):
    def __init__(self, step, type, receiver, order):
        self.receiver = receiver
        self.order = order
        self.type_cn = ITEM_ACTION_CN[type]
        self.next_step = AdItem.get_next_step(step, type)
        self.agree = type in ITEM_STATUS_AGREE_ACTION
