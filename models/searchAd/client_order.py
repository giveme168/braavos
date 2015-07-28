# -*- encoding: utf-8 -*-
from models.client_order import ClientOrder, BackMoney, ClientOrderReject


class searchAdClientOrder(ClientOrder):
    __tablename__ = 'searchAd_client_order'


class searchAdBackMoney(BackMoney):
    __tablename__ = 'searchAd_client_order_back_money'


class searchAdClientOrderReject(ClientOrderReject):
    __tablename__ = 'searchAd_client_order_reject'
