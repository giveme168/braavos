# -*- coding: utf-8 -*-
import itertools
from datetime import timedelta

from . import db, BaseModelMixin
from .consts import STATUS_CN, DATE_FORMAT
from models.mixin.delivery import DeliveryMixin
from models.item import OCCUPY_RESOURCE_STATUS, ITEM_STATUS_ORDER

TARGET_TOP = 1
TARGET_BLANK = 0
TARGET_CN = {
    TARGET_TOP: u"_top",
    TARGET_BLANK: u"_blank"
}

POSITION_LEVEL_A1 = 11
POSITION_LEVEL_A2 = 12
POSITION_LEVEL_B = 21
POSITION_LEVEL_C = 31
POSITION_LEVEL_Y = 41
POSITION_LEVEL_APP = 51
POSITION_LEVEL_CN = {
    POSITION_LEVEL_A1: u"A1",
    POSITION_LEVEL_A2: u"A2",
    POSITION_LEVEL_B: u"B",
    POSITION_LEVEL_C: u"C",
    POSITION_LEVEL_Y: u"软性资源",
    POSITION_LEVEL_APP: u"APP",
}
LAUNCH_STRATEGY_A = 0
LAUNCH_STRATEGY_B = 1
LAUNCH_STRATEGY = {
    LAUNCH_STRATEGY_A: u"不可定向",
    LAUNCH_STRATEGY_B: u"定向投放(地域/精准)"
}
AD_TYPE_NORMAL = 0
AD_TYPE_CPD = 1
AD_TYPE_REMNANT = 2

AD_TYPE_CN = {
    AD_TYPE_NORMAL: u"标准/CPM",
    AD_TYPE_CPD: u"CPD",
}

EMPTY = 0
TWENTY_FIVE = 25
FIFTY = 50
SEVENTY_FIVE = 75
HUNDERD = 100
ERROR = 101

OCCUPY_RESOURCE_PRECENT_CN = {
    EMPTY: "",
    TWENTY_FIVE: "twenty-five",
    FIFTY: "fifty",
    SEVENTY_FIVE: "seventy-five",
    HUNDERD: "hundred",
    ERROR: "error"
}

ad_position_unit_table = db.Table('ad_position_unit',
                                  db.Column('position_id', db.Integer, db.ForeignKey('ad_position.id')),
                                  db.Column('unit_id', db.Integer, db.ForeignKey('ad_unit.id'))
                                  )


class Medium(db.Model, BaseModelMixin):
    __tablename__ = 'medium'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    owner_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    owner = db.relationship('Team', backref=db.backref('mediums', lazy='dynamic'))

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner

    def __repr__(self):
        return '<Medium %s>' % (self.name)

    def positions_info_by_date(self):
        return positions_info(self.positions)


class AdSize(db.Model, BaseModelMixin):
    __tablename__ = 'ad_size'
    id = db.Column(db.Integer, primary_key=True)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def __repr__(self):
        return "<AdSize %sx%s>" % (self.width, self.height)

    def __eq__(self, other):
        return self.width == other.width and self.height == other.height

    @property
    def name(self):
        return "%s x %s" % (self.width, self.height)


class AdUnit(db.Model, BaseModelMixin, DeliveryMixin):
    __tablename__ = 'ad_unit'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(500))
    size_id = db.Column(db.Integer, db.ForeignKey('ad_size.id'))
    size = db.relationship('AdSize', backref=db.backref('adUnits', lazy='dynamic'))
    margin = db.Column(db.String(50))
    target = db.Column(db.Integer)
    status = db.Column(db.Integer)
    medium_id = db.Column(db.Integer, db.ForeignKey('medium.id'))
    medium = db.relationship('Medium', backref=db.backref('units', lazy='dynamic'))
    estimate_num = db.Column(db.Integer)

    def __init__(self, name, description, size, margin, target, status, medium, estimate_num=0):
        self.name = name
        self.description = description
        self.size = size
        self.margin = margin
        self.target = target
        self.status = status
        self.medium = medium
        self.estimate_num = estimate_num

    def __repr__(self):
        return '<AdUnit %s>' % (self.name)

    @property
    def target_cn(self):
        return TARGET_CN[self.target]

    @property
    def status_cn(self):
        return STATUS_CN[self.status]

    @property
    def display_name(self):
        return "%s(%s)" % (self.name, self.medium.name)

    def schedule_num(self, date):
        """
        每个展示位置的的预订量按照比例分配到所拥有的广告单元上,
        再加和计算该单元的预订量
        """
        return int(round(sum([x.schedule_num(date) * (float(self.estimate_num) / x.estimate_num)
                         for x in self.positions])))

    def retain_num(self, date):
        retain_num = self.estimate_num - self.schedule_num(date)
        return max(retain_num, 0)

    def schedule_nums_by_dates(self, dates_list):
        position_s_nums = [(p.schedule_nums_by_dates(dates_list), p.estimate_num) for p in self.positions]
        # 每个位置在时间段内每天分配到当前unit的预订量
        position_to_nuit_nums = []
        for nums, e_num in position_s_nums:
            position_to_nuit_nums.append([num * (float(self.estimate_num) / e_num) for num in nums])
        temp = map(list, itertools.izip(*position_to_nuit_nums))
        return [int(round(sum(num))) for num in temp]

    def retain_nums_by_dates(self, dates_list):
        schedule_nums = self.schedule_nums_by_dates(dates_list)
        return [self.estimate_num - num for num in schedule_nums]

    @property
    def order_items(self):
        """所有关联的订单项"""
        _items = []
        for p in self.positions:
            for i in p.order_items:
                _items.append(i)
        return _items

    def online_order_items_by_date(self, _date):
        return [i for i in self.order_items if i.is_online_by_date(_date)]


class AdPosition(db.Model, BaseModelMixin):
    __tablename__ = 'ad_position'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(500))
    size_id = db.Column(db.Integer, db.ForeignKey('ad_size.id'))
    size = db.relationship('AdSize', backref=db.backref('adPositions', lazy='dynamic'))
    standard = db.Column(db.String(100))
    status = db.Column(db.Integer)
    level = db.Column(db.Integer)
    units = db.relationship('AdUnit', secondary=ad_position_unit_table,
                            backref=db.backref('positions', lazy='dynamic'))
    medium_id = db.Column(db.Integer, db.ForeignKey('medium.id'))
    medium = db.relationship('Medium', backref=db.backref('positions', lazy='dynamic'))
    ad_type = db.Column(db.Integer)
    cpd_num = db.Column(db.Integer)
    max_order_num = db.Column(db.Integer)
    price = db.Column(db.Integer)
    launch_strategy = db.Column(db.Integer)

    def __init__(self, name, description, size, standard, status, medium,
                 level=POSITION_LEVEL_A1, ad_type=AD_TYPE_NORMAL, launch_strategy=1, price=0, max_order_num=0):
        self.name = name
        self.description = description
        self.size = size
        self.standard = standard
        self.status = status
        self.medium = medium
        self.level = level
        self.ad_type = ad_type
        self.price = price
        self.max_order_num = max_order_num
        self.launch_strategy = launch_strategy

    def __repr__(self):
        return '<AdPosition %s>' % (self.name)

    @property
    def status_cn(self):
        return STATUS_CN[self.status]

    @property
    def display_name(self):
        return "%s-%s-%s" % (self.name, self.level_cn, self.medium.name)

    @property
    def level_cn(self):
        return POSITION_LEVEL_CN[self.level]

    @property
    def ad_type_cn(self):
        return AD_TYPE_CN[self.ad_type]

    def is_cpd(self):
        return self.ad_type == AD_TYPE_CPD

    @property
    def estimate_num(self):
        """
        预估量是所有广告单元一天预估量的和, 表示这个位置最大投放量,
        所以拥有同相同广告单元的位置不能同时预订, 否则可能会超
        所以每个展示位置需要制定一个最大预订值
        """
        return sum([x.estimate_num for x in self.units])

    @property
    def estimate_num_per_cpd(self):
        """
        平均每个CPD的预估量
        """
        return self.estimate_num / self.cpd_num if self.cpd_num > 1 else self.estimate_num

    @property
    def standard_cn(self):
        return "%s-%s" % (self.size.name, self.standard)

    def schedules_by_date(self, _date):
        return [x.schedule_by_date(_date)
                for x in self.order_items if x.schedule_by_date(_date)]

    def schedule_num(self, _date):
        """
        该位置的已经预订的量,
        通过所有预订这个位置的订单项的这一天的量计算
        """
        schedules = self.schedules_by_date(_date)
        return sum([s.num for s in schedules if s.item.item_status in OCCUPY_RESOURCE_STATUS])

    def schedule_nums_by_dates(self, dates_list):
        # 每个item在时间段内每天的已预订量
        item_nums = [
            i.schedule_sums_by_dates(dates_list) for i in self.order_items
            if i.item_status in OCCUPY_RESOURCE_STATUS]
        temp = map(list, itertools.izip(*item_nums))
        return [sum(d) for d in temp]

    def ordered_num(self, _date):
        """该位置的已经下单的量"""
        schedules = self.schedules_by_date(_date)
        return sum([s.num for s in schedules if s.item.item_status == ITEM_STATUS_ORDER])

    @property
    def suitable_units(self):
        return AdUnit.query.filter_by(medium_id=self.medium.id, size=self.size)

    def retain_num(self, date):
        """剩余量, 所有广告单元的剩余量"""
        return sum([x.retain_num(date) for x in self.units])

    def can_order_num(self, date):
        """可预订量"""
        return min(self.max_order_num, self.retain_num(date))

    def check_order_num(self, date, num):
        return num <= self.order_num(date)

    def can_order_num_schedule(self, start_date, end_date):
        """在start和end之间可以预订的量"""
        days = (end_date - start_date).days + 1
        schedules = [(start_date + timedelta(days=n), self.can_order_num(start_date + timedelta(days=n)))
                     for n in range(days)]
        return schedules

    def get_schedule(self, start_date, end_date):
        """格式化预订量"""
        ret = {"position": self.id,
               "name": self.display_name,
               "start": start_date.strftime(DATE_FORMAT),
               "end": end_date.strftime(DATE_FORMAT)}
        ret['schedules'] = [schdule_info(_date, num)
                            for _date, num in self.can_order_num_schedule(start_date, end_date)]
        return ret

    def storage_percent_cn(self, percent):
        if percent == EMPTY:
            return OCCUPY_RESOURCE_PRECENT_CN[EMPTY]
        elif percent <= TWENTY_FIVE:
            return OCCUPY_RESOURCE_PRECENT_CN[TWENTY_FIVE]
        elif percent <= FIFTY:
            return OCCUPY_RESOURCE_PRECENT_CN[FIFTY]
        elif percent <= SEVENTY_FIVE:
            return OCCUPY_RESOURCE_PRECENT_CN[SEVENTY_FIVE]
        elif percent <= HUNDERD:
            return OCCUPY_RESOURCE_PRECENT_CN[HUNDERD]
        else:
            return OCCUPY_RESOURCE_PRECENT_CN[ERROR]

    def storage_percent_info(self, start_date, last):
        """得到一个（预订百分比区间，日期）的列表"""
        dates_list = []
        for x in range(0, last):
            current = start_date + timedelta(days=x)
            dates_list.append(current)
        current_nums = self.schedule_nums_by_dates(dates_list)
        units_retains = [u.retain_nums_by_dates(dates_list) for u in self.units]
        temp = map(list, itertools.izip(*units_retains))
        retain_nums = [sum(d) for d in temp]
        storage_info = []
        for i in range(0, last):
            min_num = 1 if current_nums[i] > 0 else 0
            percent = max([current_nums[i] * 100 / (retain_nums[i] + current_nums[i]), min_num])
            storage_info.append((self.storage_percent_cn(percent), dates_list[i]))
        return storage_info

    def get_storage_info(self, date):
        ret = {"position": self.id,
               "estimate_num": self.estimate_num,
               "ordered_num": self.ordered_num(date),
               "per_ordered_num": self.schedule_num(date) - self.ordered_num(date),
               "remain_num": self.retain_num(date)}
        ret['orders'] = [order_info(o, self, date) for o in self.get_orders_by_date(date)]
        return ret

    def get_orders_by_date(self, date):
        orders = [i.order for i in self.order_items if i.schedule_by_date(date)]
        return list(set(orders))

    @classmethod
    def all_positions_info_by_date(cls):
        return positions_info(cls.all())


def positions_info(positions):
    positions_info = []
    level_dict = sorted(POSITION_LEVEL_CN.iteritems(), key=lambda d: d[0])
    for v, level_cn in level_dict:
        temp_positions = [p for p in positions if p.level == v]
        positions_info.append((v, POSITION_LEVEL_CN[v], temp_positions))
    return positions_info


def schdule_info(date, num):
    return (date.strftime(DATE_FORMAT), num, date.isoweekday())


def order_info(order, position, date):
    order_info_dic = {}
    order_info_dic["name"] = order.name
    order_info_dic["URL"] = order.path()
    order_info_dic["occupy_num"] = order.occupy_num_by_date_position(date, position)
    order_info_dic["state_cn"] = "&".join(order.items_status_cn)
    order_info_dic["date_cn"] = u"%s至%s" % (order.start_date_cn, order.end_date_cn)
    order_info_dic["special_sale"] = u"是" if order.special_sale_in_position(position) else u"否"
    order_info_dic["creator"] = order.creator.name
    return order_info_dic
