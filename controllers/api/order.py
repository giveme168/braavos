# -*- coding: UTF-8 -*-
import json
from flask import Blueprint, request, jsonify

from models.client_order import ClientOrder
from models.douban_order import DoubanOrder
from models.order import Order
from models.associated_douban_order import AssociatedDoubanOrder

api_bp = Blueprint('api', __name__)


def _order_to_dict(order, ass_order=None):
    param = {}
    if order.__tablename__ == 'bra_client_order':
        param['type'] = 'client_order'
    elif ass_order:
        param['type'] = 'ass_douban_order'
    else:
        param['type'] = 'douban_order'
    param['id'] = order.id
    param['campaign'] = order.campaign
    param['agent'] = order.agent.name
    param['client'] = order.client.name
    param['contract'] = order.contract
    param['money'] = order.money
    param['start_time'] = order.client_start.strftime('%Y-%m-%d')
    param['end_time'] = order.client_end.strftime('%Y-%m-%d')
    param['direct_sales'] = order.direct_sales_names
    param['agent_sales'] = order.agent_sales_names
    param['resource_type'] = order.resource_type_cn
    if ass_order:
        param['real_agent'] = ass_order.medium_order.medium.name
    else:
        param['real_agent'] = ''
    return param


@api_bp.route('/order', methods=['GET'])
def order():
    sn = request.values.get('sn', '')
    client_order = [_order_to_dict(k) for k in ClientOrder.all() if k.contract.lower().strip() == sn.lower().strip()]
    douban_order = [_order_to_dict(k) for k in DoubanOrder.all() if k.contract.lower().strip() == sn.lower().strip()]
    client_order += [_order_to_dict(k.client_order) for k in Order.all()
                     if k.medium_contract.lower().strip() == sn.lower().strip()]
    client_order += [_order_to_dict(k.client_order, k) for k in AssociatedDoubanOrder.all()
                     if k.contract.lower().strip() == sn.lower().strip()]
    if client_order:
        return jsonify({'ret': True, 'data': client_order[0]})
    elif douban_order:
        return jsonify({'ret': True, 'data': douban_order[0]})
    else:
        return jsonify({'ret': False, 'data': {}})


def _get_order_by_type(type, id):
    if type == 'client_order':
        client_order = ClientOrder.get(id)
        if client_order:
            return _order_to_dict(client_order)
        return {}
    elif type == 'douban_order':
        douban_order = DoubanOrder.get(id)
        if douban_order:
            return _order_to_dict(douban_order)
        return {}
    elif type == 'ass_douban_order':
        client_order = ClientOrder.get(id)
        if client_order:
            return _order_to_dict(client_order, client_order.associated_douban_orders[0])
        return {}
    return {}


@api_bp.route('/search/order', methods=['POST'])
def search_order_by_json():
    data = json.loads(request.values.get('data', json.dumps([])))
    orders = []
    for k in data:
        order = _get_order_by_type(k['type'], k['id'])
        if order:
            orders.append(order)
    if orders:
        return jsonify({'ret': True, 'data': orders})
    return jsonify({'ret': False, 'data': []})


@api_bp.route('/search/<type>/<id>/order', methods=['GET'])
def search_order(type, id):
    order = _get_order_by_type(type, id)
    if order:
        return jsonify({'ret': True, 'data': order})
    return jsonify({'ret': False, 'data': {}})
