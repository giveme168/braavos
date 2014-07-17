#-*- coding: UTF-8 -*-
from . import db, BaseModelMixin

ORDER_TYPE_NORMAL = 0         # 标准广告

ORDER_TYPE_CN = {
    ORDER_TYPE_NORMAL: u"标准广告(CPM, CPD)",
}

direct_sales = db.Table('order_direct_sales',
                        db.Column('sale_id', db.Integer, db.ForeignKey('user.id')),
                        db.Column('order_id', db.Integer, db.ForeignKey('order.id'))
                        )
agent_sales = db.Table('order_agent_sales',
                       db.Column('agent_sale_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column('order_id', db.Integer, db.ForeignKey('order.id'))
                       )


class Order(db.Model, BaseModelMixin):
    __tablename__ = 'order'
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
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref=db.backref('created_orders', lazy='dynamic'))

    def __init__(self, client, campaign, medium, order_type, contract, money,
                 agent, direct_sales, agent_sales, creator):
        self.client = client
        self.campaign = campaign.title()
        self.medium = medium
        self.order_type = order_type
        self.contract = contract
        self.money = money
        self.agent = agent
        self.direct_sales = direct_sales
        self.agent_sales = agent_sales
        self.creator = creator

    def __repr__(self):
        return '<Order %s>' % (self.name)

    @property
    def name(self):
        return "%s-%s-%s" % (self.contract or u"无合同", self.client.name, self.campaign)

    @property
    def order_type_cn(self):
        return ORDER_TYPE_CN[self.order_type]
