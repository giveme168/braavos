# -*- coding: UTF-8 -*-
import datetime
from collections import defaultdict
from flask import url_for

from . import db, BaseModelMixin
from models.mixin.comment import CommentMixin
from .item import (ITEM_STATUS_CN, SALE_TYPE_CN,
                   ITEM_STATUS_LEADER_ACTIONS)


ORDER_TYPE_NORMAL = 0         # 标准广告

ORDER_TYPE_CN = {
    ORDER_TYPE_NORMAL: u"标准广告(CPM, CPD)",
}

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
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    client = db.relationship('Client', backref=db.backref('orders', lazy='dynamic'))
    campaign = db.Column(db.String(100))
    medium_id = db.Column(db.Integer, db.ForeignKey('medium.id'))
    medium = db.relationship('Medium', backref=db.backref('orders', lazy='dynamic'))
    order_type = db.Column(db.Integer)
    contract = db.Column(db.String(100))
    money = db.Column(db.Integer)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'))
    agent = db.relationship('Agent', backref=db.backref('orders', lazy='dynamic'))
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
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, client, campaign, medium, order_type, contract, money,
                 agent, direct_sales, agent_sales, operaters, designers, planers,
                 creator, create_time=None):
        self.client = client
        self.campaign = campaign
        self.medium = medium
        self.order_type = order_type
        self.contract = contract
        self.money = money
        self.agent = agent
        self.direct_sales = direct_sales
        self.agent_sales = agent_sales
        self.operaters = operaters
        self.designers = designers
        self.planers = planers
        self.creator = creator
        self.create_time = create_time

    def __repr__(self):
        return '<Order %s>' % (self.id)

    @property
    def name(self):
        return u"%s-%s-%s" % (self.contract or u"合同号暂缺", self.client.name, self.campaign)

    @property
    def order_type_cn(self):
        return ORDER_TYPE_CN[self.order_type]

    def items_by_status(self, status):
        sorted_items = sorted(self.items, lambda x, y: x.create_time > y.create_time)
        return filter(lambda x: x.item_status == status, sorted_items)

    def items_info_by_items(self, items):
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
            ret['months'] = {m: len(d_list) for m, d_list in m_dict.items()}
        else:
            ret['dates'] = []
            ret['months'] = {}
        sale_type_items = []
        for v, sale_type_cn in SALE_TYPE_CN.items():
            sale_type_items.append((v, SALE_TYPE_CN[v], [x for x in items if x.sale_type == v]))
        ret['items'] = sale_type_items
        return ret

    def items_info_by_status(self, status):
        items = self.items_by_status(status)
        ret = self.items_info_by_items(items)
        ret['status_cn'] = ITEM_STATUS_CN[status]
        return ret

    def items_info_all(self):
        ret = self.items_info_by_items(self.items)
        ret['status_cn'] = u"全部"
        return ret

    def items_info(self):
        items_info = [self.items_info_by_status(x) for x in ITEM_STATUS_CN]
        items_info.append(self.items_info_all())
        return items_info

    def can_admin(self, user):
        admin_users = self.direct_sales + self.agent_sales + self.operaters
        return any([user.is_admin(), self.creator_id == user.id, user in admin_users])

    def can_action(self, user, action):
        if action in ITEM_STATUS_LEADER_ACTIONS:
            return any([user.is_admin(), user.is_leader(), user.team == self.medium.owner])
        else:
            return self.can_admin(user)

    def path(self):
        return url_for('order.order_detail', order_id=self.id, step=0)
