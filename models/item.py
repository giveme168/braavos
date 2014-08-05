#-*- coding: UTF-8 -*-
from datetime import datetime, timedelta

from . import db, BaseModelMixin
from consts import STATUS_CN

SALE_TYPE_NORMAL = 0         # 标准, 购买
SALE_TYPE_GIFT = 1           # 配送
SALE_TYPE_REMNANT = 2         # 补量
#SALE_TYPE_CPC = 3            # CPC

SALE_TYPE_CN = {
    SALE_TYPE_NORMAL: u"标准/购买",
    SALE_TYPE_GIFT: u"配送",
    SALE_TYPE_REMNANT: u"补量",
    #SALE_TYPE_CPC: u"CPC",
}

AD_TYPE_NORMAL = 0
AD_TYPE_CPD = 1
AD_TYPE_REMNANT = 2

AD_TYPE_CN = {
    AD_TYPE_NORMAL: u"标准/CPM",
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
ITEM_STATUS_PRE_APPLY = 1
ITEM_STATUS_PRE = 2
ITEM_STATUS_ORDER_APPLY = 3
ITEM_STATUS_ORDER = 4

ITEM_STATUS_CN = {
    ITEM_STATUS_NEW: u"新建",
    ITEM_STATUS_PRE_APPLY: u"申请预下单",
    ITEM_STATUS_PRE: u"已预下单(资源已锁定)",
    ITEM_STATUS_ORDER_APPLY: u"申请下单",
    ITEM_STATUS_ORDER: u"已下单"
}


class AdItem(db.Model, BaseModelMixin):
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
    create_time = db.Column(db.DateTime, default=datetime.now())

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

    @property
    def sale_type_cn(self):
        return SALE_TYPE_CN[self.sale_type]

    @property
    def status_cn(self):
        return STATUS_CN[self.status]

    @classmethod
    def gets_by_position(cls, position):
        return cls.query.filter_by(position_id=position.id)

    @property
    def start_time(self):
        return min([s.start_time for s in self.schedules]) if self.schedules else None

    @property
    def start_time_cn(self):
        return self.start_time.strftime("%Y-%m-%d %H:%M:%S") if self.start_time else u"起始时间"

    @property
    def end_time(self):
        return min([s.end_time for s in self.schedules]) if self.schedules else None

    @property
    def end_time_cn(self):
        return self.end_time.strftime("%Y-%m-%d %H:%M:%S") if self.end_time else u"起始时间"


class AdSchedule(db.Model, BaseModelMixin):
    __tablename__ = 'bra_schedule'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('bra_item.id'))
    item = db.relationship('AdItem', backref=db.backref('schedules', lazy='dynamic'))
    num = db.Column(db.Integer)  # 投放量
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    def __init__(self, item, num, start_time, end_time):
        self.item = item
        self.num = num
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        return '<AdSchedule %s-%s-%s>' % (self.item.name, self.start_time, self.end_time)

    @property
    def units(self):
        return self.item.position.units

    @property
    def start_date(self):
        return datetime(self.start_time.year, self.start_time.month, self.start_time.day)

    @property
    def end_date(self):
        return datetime(self.end_time.year, self.end_time.month, self.end_time.day)

    @property
    def total_seconds(self):
        return (self.end_time - self.start_time).total_seconds()

    @property
    def firstday_secounds(self):
        if self.end_date > self.start_date:
            return (self.start_date + timedelta(days=1) - self.start_time).total_seconds()
        else:
            return self.total_seconds

    @property
    def lastday_secounds(self):
        if self.end_date > self.start_date:
            return (self.end_time - self.end_date).total_seconds()
        else:
            return self.total_seconds

    def num_by_date(self, date):
        """计算平均分配到每天的投放量"""
        if date < self.start_date or date > self.end_date:  # 不在日期内
            return 0
        elif date == self.start_date and date == self.end_date:  # 投放开始结束在同一天
            return self.num
        elif date == self.start_date:  # 第一天
            return int(self.num * self.firstday_secounds / self.total_seconds)
        elif date == self.end_date:  # 最后一天
            return int(self.num * self.lastday_secounds / self.total_seconds)
        else:  # 其中某一天
            return int(self.num * timedelta(days=1).total_secounds / self.total_seconds)
