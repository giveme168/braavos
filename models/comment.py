# -*- coding: UTF-8 -*-
import datetime

from . import db, BaseModelMixin


##################
# msg_channel type
# 0 : 合同
# 1 : 客户发票
# 2 : 外包项
# 3 : 媒体发票与打款
# 4 : 回款
# 5 : 甲方打款与发票
# 6 : 媒体资料
# 7 : 策划单
# 8 : 媒体返点回款
# 9 : 设置代理返点
# 10: 杂项成本
# 11: 洽谈中的订单
# 12: 对账单
# 13: 代理信息
# 14：媒体信息
##################
class Comment(db.Model, BaseModelMixin):
    __tablename__ = 'bra_comment'
    id = db.Column(db.Integer, primary_key=True)
    target_type = db.Column(db.String(50))
    target_id = db.Column(db.Integer)
    msg_channel = db.Column(db.Integer, default=0)
    msg = db.Column(db.String(1000))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, target_type, target_id, msg, creator,
                 create_time=None, msg_channel=0):
        self.target_type = target_type
        self.target_id = target_id
        self.msg = msg
        self.creator = creator
        self.create_time = create_time
        self.msg_channel = msg_channel

    def __repr__(self):
        return '<Comment %s, target:%s-%s>' % (self.id, self.target_type, self.target_id)

    @property
    def target(self):
        from .order import Order
        from .client import Agent
        from .client_order import ClientOrder, IntentionOrder
        from .client_medium_order import ClientMediumOrder
        from .douban_order import DoubanOrder
        from .framework_order import FrameworkOrder
        from .medium_framework_order import MediumFrameworkOrder
        from .item import AdItem
        from .material import Material
        from searchAd.models.order import searchAdOrder
        from searchAd.models.client_order import searchAdClientOrder, searchAdClientOrderBill
        from searchAd.models.rebate_order import searchAdRebateOrder
        from models.medium import Medium
        from models.planning import Bref
        TARGET_DICT = {
            'Order': Order,
            'DoubanOrder': DoubanOrder,
            'ClientOrder': ClientOrder,
            'ClientMediumOrder': ClientMediumOrder,
            'FrameworkOrder': FrameworkOrder,
            'MediumFrameworkOrder': MediumFrameworkOrder,
            'AdItem': AdItem,
            'Material': Material,
            'searchAdOrder': searchAdOrder,
            'searchAdClientOrder': searchAdClientOrder,
            'searchAdRebateOrder': searchAdRebateOrder,
            'Medium': Medium,
            'Bref': Bref,
            'Agent': Agent,
            'IntentionOrder': IntentionOrder,
            'searchAdClientOrderBill': searchAdClientOrderBill,
        }
        return TARGET_DICT[self.target_type].get(self.target_id)
