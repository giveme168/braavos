# -*- coding: UTF-8 -*-
import datetime
from collections import defaultdict
from flask import url_for
from xlwt import Utils

from . import db, BaseModelMixin
from models.mixin.comment import CommentMixin
from models.mixin.attachment import AttachmentMixin
from models.attachment import ATTACHMENT_STATUS_PASSED, ATTACHMENT_STATUS_REJECT
from .item import (ITEM_STATUS_CN, SALE_TYPE_CN,
                   ITEM_STATUS_LEADER_ACTIONS, OCCUPY_RESOURCE_STATUS,
                   ITEM_STATUS_PRE, ITEM_STATUS_PRE_PASS, ITEM_STATUS_ORDER_APPLY,
                   ITEM_STATUS_ORDER)
from .client_order import table_medium_orders, ClientOrder
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
# DISCOUNT_SELECT = 0

DISCOUNT_CN = {
    DISCOUNT_50: u'5折',
    DISCOUNT_60: u'6折',
    DISCOUNT_70: u'7折',
    DISCOUNT_GIFT: u'配送',
    DISCOUNT_ADD: u'无折扣',
}

DISCOUNT_SALE = {
    # DISCOUNT_SELECT: u'请选择',
    DISCOUNT_50: u'5折',
    DISCOUNT_60: u'6折',
    DISCOUNT_70: u'7折',
    DISCOUNT_ADD: u'无折扣',
}


HEADER_BEFORE_DATE = [u"售卖类型", u"预订状态", u"展示位置", u"广告标准"]
HEADER_AFTER_DATE = [u"总预订量", u"刊例单价", u"刊例总价", u"折扣", u"净价"]

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


class Order(db.Model, BaseModelMixin, CommentMixin, AttachmentMixin):
    __tablename__ = 'bra_order'

    id = db.Column(db.Integer, primary_key=True)
    campaign = db.Column(db.String(100))  # 活动名称
    medium_id = db.Column(db.Integer, db.ForeignKey('medium.id'))  # 投放媒体
    medium = db.relationship('Medium', backref=db.backref('orders', lazy='dynamic'))
    order_type = db.Column(db.Integer)  # 订单类型: CPM

    client_orders = db.relationship('ClientOrder', secondary=table_medium_orders)

    medium_contract = db.Column(db.String(100))  # 媒体合同号
    medium_money = db.Column(db.Integer)  # 下单金额
    medium_money2 = db.Column(db.Integer)  # 未分成金额
    sale_money = db.Column(db.Integer)  # 售卖金额
    medium_CPM = db.Column(db.Integer)  # 实际CPM
    sale_CPM = db.Column(db.Integer)  # 下单CPM
    discount = db.Column(db.Integer)  # 折扣类型
    medium_start = db.Column(db.Date)
    medium_end = db.Column(db.Date)

    operaters = db.relationship('User', secondary=operater_users)
    designers = db.relationship('User', secondary=designer_users)
    planers = db.relationship('User', secondary=planer_users)

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref=db.backref('created_orders', lazy='dynamic'))
    create_time = db.Column(db.DateTime)

    contract_generate = True
    kind = "medium-order"

    def __init__(self, campaign, medium, order_type=ORDER_TYPE_NORMAL,
                 medium_contract="", medium_money=0, sale_money=0, medium_money2=0,
                 medium_CPM=0, sale_CPM=0,
                 discount=DISCOUNT_ADD, medium_start=None, medium_end=None,
                 operaters=None, designers=None, planers=None,
                 creator=None, create_time=None):
        self.campaign = campaign
        self.medium = medium
        self.order_type = order_type

        self.medium_contract = medium_contract
        self.medium_money = medium_money
        self.medium_money2 = medium_money2
        self.sale_money = sale_money
        self.medium_CPM = medium_CPM
        self.sale_CPM = sale_CPM
        self.discount = discount
        self.medium_start = medium_start or datetime.date.today()
        self.medium_end = medium_end or datetime.date.today()

        self.operaters = operaters or []
        self.designers = designers or []
        self.planers = planers or []

        self.creator = creator
        self.create_time = create_time or datetime.datetime.now()

    def __repr__(self):
        return '<Order %s>' % (self.id)

    @property
    def sale_ECPM(self):
        return (self.medium_money2 / float(self.sale_CPM)) if (self.medium_money2 and self.sale_CPM) else 0

    @property
    def money_rate(self):
        """利润率"""
        if (self.sale_money and self.medium_money):
            return (self.sale_money - self.medium_money) / float(self.sale_money)
        else:
            return 0

    @property
    def name(self):
        return self.medium.name

    @property
    def client_order(self):
        return ClientOrder.get(self.client_orders[0].id)

    @property
    def operater_names(self):
        return ",".join([u.name for u in self.operaters])

    @property
    def designers_names(self):
        return ",".join([u.name for u in self.designers])

    @property
    def planers_names(self):
        return ",".join([u.name for u in self.planers])

    @property
    def contract_status(self):
        return self.client_order.contract_status

    @property
    def order_type_cn(self):
        return ORDER_TYPE_CN[self.order_type]

    @property
    def email_info(self):
        return u"""
        投放媒体: %s
        售卖金额: %s (元)
        媒体金额: %s (元)
        预估CPM: %s
        预估ECPM: %.1f 媒体金额/预估CPM
        执行: %s
        """ % (self.medium.name, self.sale_money or 0, self.medium_money2 or 0,
               self.sale_CPM or 0, self.sale_ECPM, self.operater_names)

    @property
    def direct_sales(self):
        direct_sales = []
        for k in self.client_orders:
            direct_sales += k.direct_sales
        return direct_sales

    @property
    def agent_sales(self):
        agent_sales = []
        for k in self.client_orders:
            agent_sales += k.agent_sales
        return agent_sales

    def can_admin(self, user):
        """是否可以修改该订单"""
        admin_users = self.operaters + [self.creator]
        return user.is_media() or self.client_order.can_admin(user) or user in admin_users

    def can_action(self, user, action):
        """是否拥有leader操作"""
        if action in ITEM_STATUS_LEADER_ACTIONS:
            return any([user.is_admin(), user.is_leader()])
        else:
            return self.can_admin(user)

    def have_owner(self, user):
        """是否可以查看该订单"""
        owner = self.operaters + self.designers + self.planers + [self.creator]
        return user.is_admin() or user in owner or self.client_order.have_owner(user)

    def path(self):
        return url_for('schedule.order_detail', order_id=self.id, step=0)

    def edit_path(self):
        return url_for('order.medium_order', mo_id=self.id)

    def attachment_path(self):
        return url_for('files.medium_order_files', order_id=self.id)

    def info_path(self):
        return self.client_order.info_path()

    def attach_status_confirm_path(self, attachment):
        return url_for('order.medium_attach_status',
                       order_id=self.id,
                       attachment_id=attachment.id,
                       status=ATTACHMENT_STATUS_PASSED)

    def attach_status_reject_path(self, attachment):
        return url_for('order.medium_attach_status',
                       order_id=self.id,
                       attachment_id=attachment.id,
                       status=ATTACHMENT_STATUS_REJECT)

    @classmethod
    def contract_exist(cls, contract):
        is_exist = cls.query.filter_by(medium_contract=contract).count() > 0
        return is_exist

    def get_default_contract(self):
        return contract_generator(self.medium.current_framework, self.id)

    @property
    def start_date(self):
        return self.medium_start

    @property
    def start_date_cn(self):
        return self.start_date.strftime(DATE_FORMAT)

    @property
    def end_date(self):
        return self.medium_end

    @property
    def end_date_cn(self):
        return self.end_date.strftime(DATE_FORMAT)

    """订单项相关"""
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

    def occupy_num_by_date_position(self, date, position):
        return sum(
            [i.schedule_sum_by_date(date) for i in self.items
             if i.item_status in OCCUPY_RESOURCE_STATUS and i.position == position])

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

    def delete(self):
        self.delete_comments()
        self.delete_attachments()
        for ao in self.associated_douban_orders:
            ao.delete()
        db.session.delete(self)
        db.session.commit()

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
        ret['months'] = {m: len(d_list) for (m, d_list) in m_dict.items()}
    else:
        ret['dates'] = []
        ret['months'] = {}
    sale_type_items = []
    for v, sale_type_cn in SALE_TYPE_CN.items():
        sale_type_items.append((v, SALE_TYPE_CN[v], [x for x in items if x.sale_type == v]))
    ret['items'] = sale_type_items
    return ret


def contract_generator(framework, num):
    code = "%s-%03x" % (framework, num % 1000)
    code = code.upper()
    return code
