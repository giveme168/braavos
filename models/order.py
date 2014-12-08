# -*- coding: UTF-8 -*-
import datetime
from collections import defaultdict
from flask import url_for
from xlwt import Utils

from . import db, BaseModelMixin
from models.mixin.comment import CommentMixin
from .item import (ITEM_STATUS_CN, SALE_TYPE_CN,
                   ITEM_STATUS_LEADER_ACTIONS, OCCUPY_RESOURCE_STATUS,
                   ITEM_STATUS_PRE, ITEM_STATUS_PRE_PASS, ITEM_STATUS_ORDER_APPLY,
                   ITEM_STATUS_ORDER)
from models.excel import (
    ExcelCellItem, StyleFactory, EXCEL_DATA_TYPE_MERGE,
    EXCEL_DATA_TYPE_STR, EXCEL_DATA_TYPE_FORMULA,
    EXCEL_DATA_TYPE_NUM, COLOUR_RED, COLOUR_LIGHT_GRAY)
from consts import DATE_FORMAT


ORDER_TYPE_NORMAL = 0         # 标准广告

ORDER_TYPE_CN = {
    ORDER_TYPE_NORMAL: u"标准广告(CPM, CPD)",
}

DISCOUNT_70 = 70
DISCOUNT_60 = 60
DISCOUNT_50 = 50
DISCOUNT_GIFT = 0
DISCOUNT_ADD = 100
DISCOUNT_SELECT = 0

DISCOUNT_CN = {
    DISCOUNT_50: u'5折',
    DISCOUNT_60: u'6折',
    DISCOUNT_70: u'7折',
    DISCOUNT_GIFT: u'配送',
    DISCOUNT_ADD: u'无折扣',
}

DISCOUNT_SALE = {
    DISCOUNT_SELECT: u'请选择',
    DISCOUNT_50: u'5折',
    DISCOUNT_60: u'6折',
    DISCOUNT_70: u'7折',
    DISCOUNT_ADD: u'无折扣',
}

CONTRACT_TYPE_NORMAL = 0
CONTRACT_TYPE_SPECIAL = 1
CONTRACT_TYPE_CN = {
    CONTRACT_TYPE_NORMAL: u"标准",
    CONTRACT_TYPE_SPECIAL: u"非标"
}

RESOURCE_TYPE_AD = 0
RESOURCE_TYPE_CAMPAIGN = 1
RESOURCE_TYPE_FRAME = 2
RESOURCE_TYPE_OTHER = 4
RESOURCE_TYPE_CN = {
    RESOURCE_TYPE_AD: u"硬广",
    RESOURCE_TYPE_CAMPAIGN: u"互动",
    RESOURCE_TYPE_FRAME: u"框架",
    RESOURCE_TYPE_OTHER: u"其他"
}

CONTRACT_STATUS_NEW = 0
CONTRACT_STATUS_APPLYCONTRACT = 1
CONTRACT_STATUS_APPLYPASS = 2
CONTRACT_STATUS_APPLYREJECT = 3
CONTRACT_STATUS_APPLYPRINT = 4
CONTRACT_STATUS_PRINTED = 5
CONTRACT_STATUS_CN = {
    CONTRACT_STATUS_NEW: u"新建",
    CONTRACT_STATUS_APPLYCONTRACT: u"申请合同号中...",
    CONTRACT_STATUS_APPLYPASS: u"申请合同号通过",
    CONTRACT_STATUS_APPLYREJECT: u"申请合同号未通过",
    CONTRACT_STATUS_APPLYPRINT: u"申请打印中...",
    CONTRACT_STATUS_PRINTED: u"打印完毕"
}

HEADER_BEFORE_DATE = [u"售卖类型", u"预订状态", u"展示位置", u"广告标准"]
HEADER_AFTER_DATE = [u"总预订量", u"刊例单价", u"刊例总价", u"折扣", u"净价"]

direct_sales = db.Table('order_direct_sales',
                        db.Column('sale_id', db.Integer, db.ForeignKey('user.id')),
                        db.Column('order_id', db.Integer, db.ForeignKey('bra_order.id'))
                        )
agent_sales = db.Table('order_agent_sales',
                       db.Column('agent_sale_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column('order_id', db.Integer, db.ForeignKey('bra_order.id'))
                       )
operater_users = db.Table('order_users_operater',
                          db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                          db.Column('order_id', db.Integer, db.ForeignKey('bra_order.id'))
                          )
designer_users = db.Table('order_users_designerer',
                          db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                          db.Column('order_id', db.Integer, db.ForeignKey('bra_order.id'))
                          )
planer_users = db.Table('order_users_planer',
                        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                        db.Column('order_id', db.Integer, db.ForeignKey('bra_order.id'))
                        )


class Order(db.Model, BaseModelMixin, CommentMixin):
    __tablename__ = 'bra_order'

    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'))  # 客户合同甲方
    agent = db.relationship('Agent', backref=db.backref('orders', lazy='dynamic'))
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))  # 客户
    client = db.relationship('Client', backref=db.backref('orders', lazy='dynamic'))
    campaign = db.Column(db.String(100))  # 活动名称
    medium_id = db.Column(db.Integer, db.ForeignKey('medium.id'))  # 投放媒体
    medium = db.relationship('Medium', backref=db.backref('orders', lazy='dynamic'))
    order_type = db.Column(db.Integer)  # 订单类型: CPM
    
    contract = db.Column(db.String(100))  # 客户合同号
    money = db.Column(db.Integer)  # 客户合同金额
    contract_type = db.Column(db.Integer)  # 合同类型： 标准，非标准
    client_start = db.Column(db.Date)
    client_end = db.Column(db.Date)
    reminde_date = db.Column(db.Date)  # 最迟回款日期
    resource_type = db.Column(db.Integer)  # 资源形式

    medium_contract = db.Column(db.String(100))  # 媒体合同号
    medium_money = db.Column(db.Integer)  # 媒体合同金额
    discount = db.Column(db.Integer)  # 折扣类型
    medium_start = db.Column(db.Date)
    medium_end = db.Column(db.Date)
    contract_status = db.Column(db.Integer)  # 合同审批状态

    direct_sales = db.relationship('User', secondary=direct_sales,
                                   backref=db.backref('direct_orders', lazy='dynamic'))
    agent_sales = db.relationship('User', secondary=agent_sales,
                                  backref=db.backref('agent_orders', lazy='dynamic'))
    operaters = db.relationship('User', secondary=operater_users,
                                backref=db.backref('operate_orders', lazy='dynamic'))
    designers = db.relationship('User', secondary=designer_users,
                                backref=db.backref('design_orders', lazy='dynamic'))
    planers = db.relationship('User', secondary=planer_users,
                              backref=db.backref('plan_orders', lazy='dynamic'))

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref=db.backref('created_orders', lazy='dynamic'))
    create_time = db.Column(db.DateTime)

    def __init__(self, agent, client, campaign, medium, order_type=ORDER_TYPE_NORMAL,
                 contract="", money=0, contract_type=CONTRACT_TYPE_NORMAL, client_start=None, client_end=None, reminde_date=None, resource_type=RESOURCE_TYPE_AD,
                 medium_contract="", medium_money=0, discount=DISCOUNT_ADD, medium_start=None, medium_end=None,
                 direct_sales=None, agent_sales=None, operaters=None, designers=None, planers=None,
                 creator=None, create_time=None, contract_status=CONTRACT_STATUS_NEW):
        self.agent = agent
        self.client = client
        self.campaign = campaign
        self.medium = medium
        self.order_type = order_type

        self.contract = contract
        self.money = money
        self.contract_type = contract_type
        self.client_start = client_start or datetime.date.today()
        self.client_end = client_end or datetime.date.today()
        self.reminde_date = reminde_date or datetime.date.today()

        self.medium_contract = medium_contract
        self.medium_money = medium_money
        self.discount = discount
        self.medium_start = medium_start or datetime.date.today()
        self.medium_end = medium_end or datetime.date.today()

        self.direct_sales = direct_sales or []
        self.agent_sales = agent_sales or []
        self.operaters = operaters or []
        self.designers = designers or []
        self.planers = planers or []

        self.creator = creator
        self.create_time = create_time or datetime.datetime.now()
        self.contract_status = contract_status

    def __repr__(self):
        return '<Order %s>' % (self.id)

    @property
    def name(self):
        return u"%s-%s-%s" % (self.client.name, self.campaign, self.medium.name)

    @property
    def order_type_cn(self):
        return ORDER_TYPE_CN[self.order_type]

    @classmethod
    def all_per_order(cls):
        """ 所有预下单的订单 """
        return [o for o in cls.all() if len(o.pre_items)]

    @property
    def pre_items(self):
        """预下单的订单项"""
        sorted_items = sorted(self.items, lambda x, y: x.create_time > y.create_time)
        return filter(
            lambda x: x.item_status in [ITEM_STATUS_PRE, ITEM_STATUS_PRE_PASS, ITEM_STATUS_ORDER_APPLY],
            sorted_items)

    def items_by_status(self, status):
        """某个状态的订单项"""
        sorted_items = sorted(self.items, lambda x, y: x.create_time > y.create_time)
        return filter(lambda x: x.item_status == status, sorted_items)

    def items_status_num(self, num):
        return len(self.items_by_status(num))

    def items_info_by_status(self, status):
        """某个状态的订单项的格式化信息"""
        items = self.items_by_status(status)
        ret = items_info_by_items(items)
        ret['status_cn'] = ITEM_STATUS_CN[status]
        return ret

    def items_info_all(self):
        """全部订单项的格式化信息"""
        ret = items_info_by_items(self.items)
        ret['status_cn'] = u"全部"
        return ret

    def items_info(self):
        items_info = [self.items_info_by_status(x) for x in ITEM_STATUS_CN]
        items_info.append(self.items_info_all())
        return items_info

    def can_admin(self, user):
        """是否可以修改该订单"""
        admin_users = self.direct_sales + self.agent_sales + self.operaters
        return any([user.is_admin(), self.creator_id == user.id, user in admin_users])

    def can_action(self, user, action):
        """是否拥有leader操作"""
        if action in ITEM_STATUS_LEADER_ACTIONS:
            return any([user.is_admin(), user.is_leader(), user.team == self.medium.owner])
        else:
            return self.can_admin(user)

    def have_owner(self, user):
        """是否可以查看该订单"""
        owner = self.direct_sales + self.agent_sales + self.operaters + self.designers + self.planers
        return any([user.is_admin(), self.creator_id == user.id, user in owner])

    @classmethod
    def get_order_by_user(cls, user):
        """一个用户可以查看的所有订单"""
        return [o for o in cls.all() if o.have_owner(user)]

    def path(self):
        return url_for('order.order_detail', order_id=self.id, step=0)

    @property
    def start_date(self):
        start_dates = [i.start_date for i in self.items]
        return min(start_dates) if start_dates else datetime.date(1900, 1, 1)

    @property
    def start_date_cn(self):
        return self.start_date.strftime(DATE_FORMAT) if self.start_date != datetime.date(1900, 1, 1) else u"无订单项"

    @property
    def end_date(self):
        end_dates = [i.end_date for i in self.items]
        return max(end_dates) if end_dates else datetime.date(1900, 1, 1)

    @property
    def end_date_cn(self):
        return self.end_date.strftime(DATE_FORMAT) if self.end_date != datetime.date(1900, 1, 1) else u"无订单项"

    def occupy_num_by_date_position(self, date, position):
        return sum(
            [i.schedule_sum_by_date(date) for i in self.items
             if i.item_status in OCCUPY_RESOURCE_STATUS and i.position == position])

    @property
    def contract_status_cn(self):
        return CONTRACT_STATUS_CN[self.contract_status]

    @property
    def items_status(self):
        """所有订单项的状态"""
        return list(set([i.item_status for i in self.items]))

    @property
    def items_status_cn(self):
        """只关心预下单状态和已下单状态"""
        items_status_cn = []
        if (ITEM_STATUS_PRE in self.items_status
            or ITEM_STATUS_PRE_PASS in self.items_status
                or ITEM_STATUS_ORDER_APPLY in self.items_status):
            items_status_cn.append(u'预下单')
        if ITEM_STATUS_ORDER in self.items_status:
            items_status_cn.append(u'已下单')
        return items_status_cn

    def status_cn_by_status(self, status):
        return ITEM_STATUS_CN[status]

    def special_sale_in_position(self, position):
        special_sale_items = [i for i in self.items if i.position == position and i.special_sale]
        return len(special_sale_items)

    @property
    def excel_table(self):
        items_info = self.items_info_all()
        excel_table = []
        temp_row = []
        data_start_row = 2
        data_start_col = 4
        # 表头
        for header_cn in HEADER_BEFORE_DATE:
            temp_row.append(
                ExcelCellItem(EXCEL_DATA_TYPE_STR, header_cn, StyleTypes.header, 1, 0))
        for m, m_len in items_info['months'].items():
            temp_row.append(
                ExcelCellItem(EXCEL_DATA_TYPE_NUM, str(m) + u"月", StyleTypes.header, 0, m_len - 1))
            for i in range(0, m_len - 1):
                temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_MERGE))
        for header_cn in HEADER_AFTER_DATE:
            temp_row.append(
                ExcelCellItem(EXCEL_DATA_TYPE_STR, header_cn, StyleTypes.header, 1, 0))
        excel_table.append(temp_row)  # 第一行写完
        temp_row = []
        for i in range(0, len(HEADER_BEFORE_DATE)):
            temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_MERGE))
        for d in items_info['dates']:
            if d.isoweekday() in [6, 7]:
                temp_row.append(
                    ExcelCellItem(EXCEL_DATA_TYPE_NUM, d.day, StyleTypes.base_weekend))
            else:
                temp_row.append(
                    ExcelCellItem(EXCEL_DATA_TYPE_NUM, d.day, StyleTypes.base))
        for i in range(0, len(HEADER_AFTER_DATE)):
            temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_MERGE))
        excel_table.append(temp_row)  # 第二行写完
        # 填表
        temp_row = []
        for v, sale_type_cn, sale_type_items in items_info['items']:
            if not len(sale_type_items):
                break
            if sale_type_cn == u"配送":
                item_type = StyleTypes.gift
                item_weekend_type = StyleTypes.gift_weekend
            else:
                item_type = StyleTypes.base
                item_weekend_type = StyleTypes.base_weekend
            temp_row.append(
                ExcelCellItem(EXCEL_DATA_TYPE_STR, sale_type_cn, item_type, len(sale_type_items) - 1, 0))
            index = 1
            for item in sale_type_items:
                if index != 1:
                    temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_MERGE))
                temp_row.append(
                    ExcelCellItem(EXCEL_DATA_TYPE_STR, ITEM_STATUS_CN[item.item_status], item_type))
                temp_row.append(
                    ExcelCellItem(EXCEL_DATA_TYPE_STR, item.position.name, item_type))
                temp_row.append(
                    ExcelCellItem(EXCEL_DATA_TYPE_STR, item.position.standard_cn, item_type))
                for i in range(0, len(items_info['dates'])):
                    d = items_info['dates'][i]
                    if d.isoweekday() in [6, 7]:
                        if item.schedule_by_date(d):
                            temp_row.append(
                                ExcelCellItem(EXCEL_DATA_TYPE_NUM, item.schedule_by_date(d).num, item_weekend_type))
                        else:
                            temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_NUM, " ", item_weekend_type))
                    else:
                        if item.schedule_by_date(d):
                            temp_row.append(
                                ExcelCellItem(EXCEL_DATA_TYPE_NUM, item.schedule_by_date(d).num, item_type))
                        else:
                            temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_NUM, " ", item_type))
                formula = 'SUM(%s:%s)' % (
                    Utils.rowcol_to_cell(data_start_row + len(excel_table) - 2, data_start_col),
                    Utils.rowcol_to_cell(data_start_row + len(excel_table) - 2, len(temp_row) - 1))
                temp_row.append(
                    ExcelCellItem(EXCEL_DATA_TYPE_FORMULA, formula, item_type))  # 总预订量
                temp_row.append(
                    ExcelCellItem(EXCEL_DATA_TYPE_NUM, item.position.price, item_type))  # 刊例单价
                formula = '%s*%s' % (
                    Utils.rowcol_to_cell(data_start_row + len(excel_table) - 2, len(temp_row) - 2),
                    Utils.rowcol_to_cell(data_start_row + len(excel_table) - 2, len(temp_row) - 1))
                temp_row.append(
                    ExcelCellItem(EXCEL_DATA_TYPE_FORMULA, formula, item_type))  # 刊例总价
                if sale_type_cn == u"配送":
                    temp_row.append(
                        ExcelCellItem(EXCEL_DATA_TYPE_NUM, float(DISCOUNT_GIFT) / 100, StyleTypes.gift_discount))
                elif sale_type_cn == u"补量":
                    temp_row.append(
                        ExcelCellItem(EXCEL_DATA_TYPE_NUM, float(DISCOUNT_ADD) / 100, StyleTypes.discount))
                else:
                    temp_row.append(
                        ExcelCellItem(EXCEL_DATA_TYPE_NUM, float(self.discount) / 100, StyleTypes.discount))
                formula = '%s*%s' % (
                    Utils.rowcol_to_cell(data_start_row + len(excel_table) - 2, len(temp_row) - 2),
                    Utils.rowcol_to_cell(data_start_row + len(excel_table) - 2, len(temp_row) - 1))
                temp_row.append(
                    ExcelCellItem(EXCEL_DATA_TYPE_FORMULA, formula, item_type))  # 净价
                excel_table.append(temp_row)
                index += 1
                temp_row = []
        # totle
        temp_row.append(
            ExcelCellItem(EXCEL_DATA_TYPE_STR, "total", StyleTypes.base, 0, 3))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_MERGE))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_MERGE))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_MERGE))
        for i in range(0, len(items_info['dates']) + 1):
            formula = 'SUM(%s:%s)' % (
                Utils.rowcol_to_cell(data_start_row, data_start_col + i),
                Utils.rowcol_to_cell(len(excel_table) - 1, data_start_col + i))
            temp_row.append(
                ExcelCellItem(EXCEL_DATA_TYPE_FORMULA, formula, StyleTypes.base))
        temp_row.append(
            ExcelCellItem(EXCEL_DATA_TYPE_STR, "/", StyleTypes.base))
        formula = 'SUM(%s:%s)' % (
            Utils.rowcol_to_cell(data_start_row, len(temp_row)),
            Utils.rowcol_to_cell(len(excel_table) - 1, len(temp_row)))
        temp_row.append(
            ExcelCellItem(EXCEL_DATA_TYPE_FORMULA, formula, StyleTypes.base))
        temp_row.append(
            ExcelCellItem(EXCEL_DATA_TYPE_STR, "/", StyleTypes.base))
        formula = 'SUM(%s:%s)' % (
            Utils.rowcol_to_cell(data_start_row, len(temp_row)),
            Utils.rowcol_to_cell(len(excel_table) - 1, len(temp_row)))
        temp_row.append(
            ExcelCellItem(EXCEL_DATA_TYPE_FORMULA, formula, StyleTypes.base))
        excel_table.append(temp_row)
        return excel_table


class StyleTypes(object):
        """The Style of the Excel's unit"""
        base = StyleFactory().style
        header = StyleFactory().bold().style
        gift = StyleFactory().font_colour(COLOUR_RED).style
        base_weekend = StyleFactory().bg_colour(COLOUR_LIGHT_GRAY).style
        gift_weekend = StyleFactory().font_colour(COLOUR_RED).bg_colour(COLOUR_LIGHT_GRAY).style
        discount = StyleFactory().font_num('0%').style
        gift_discount = StyleFactory().font_colour(COLOUR_RED).font_num('0%').style


def items_info_by_items(items):
    ret = {}
    start_dates = [x.start_date for x in items if x.start_date]
    end_dates = [x.end_date for x in items if x.end_date]
    start = start_dates and min(start_dates)
    end = end_dates and max(end_dates)
    if start and end:
        m_dict = defaultdict(list)
        dates_list = []
        for x in range(0, (end - start).days + 1):
            current = start + datetime.timedelta(days=x)
            m_dict[current.month].append(current)
            dates_list.append(current)
        ret['dates'] = dates_list
        ret['months'] = {m:len(d_list) for (m, d_list) in m_dict.items()}
    else:
        ret['dates'] = []
        ret['months'] = {}
    sale_type_items = []
    for v, sale_type_cn in SALE_TYPE_CN.items():
        sale_type_items.append((v, SALE_TYPE_CN[v], [x for x in items if x.sale_type == v]))
    ret['items'] = sale_type_items
    return ret
