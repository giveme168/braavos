# -*- coding: UTF-8 -*-
import random
import itertools
from datetime import datetime
from flask import Blueprint, request, abort, Response, jsonify

from models.medium import Medium, AdPosition
from models.client import Client
from models.consts import DATE_FORMAT
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
    param['sale_type'] = order.sale_type_cn
    if ass_order:
        param['real_agent'] = ass_order.medium_order.medium.name
    else:
        param['real_agent'] = ''
    return param


@api_bp.route('/ad/position/<position_id>', methods=['GET'])
def ad_by_position(position_id):
    position = AdPosition.get(position_id)
    if not position:
        abort(404)
    date_str = request.values.get('date', None)
    if date_str:
        _date = datetime.strptime(date_str, DATE_FORMAT).date()
    else:
        _date = datetime.today().date()
    items = [x for x in position.order_items if x.schedule_by_date(_date)]
    if not items:
        abort(404)
    material = random.choice(
        list(itertools.chain(*[x.materials for x in items])))
    response = Response()
    response.set_data(material.html)
    return response


@api_bp.route('/mediums', methods=['GET'])
def mediums():
    mediums = [{'id': k.id, 'name': k.name} for k in Medium.all()]
    return jsonify({'data': mediums})


@api_bp.route('/clients', methods=['GET'])
def clients():
    clients = [{'id': k.id, 'name': k.name} for k in Client.all()]
    return jsonify({'data': clients})


@api_bp.route('/order', methods=['GET'])
def order():
    sn = request.values.get('sn', '')
    client_order = [_order_to_dict(k)
                                   for k in ClientOrder.all() if k.contract.lower().strip() == sn.lower().strip()]
    douban_order = [_order_to_dict(k)
                                   for k in DoubanOrder.all() if k.contract.lower().strip() == sn.lower().strip()]
    client_order += [_order_to_dict(k.client_order)
                                    for k in Order.all() if k.medium_contract.lower().strip() == sn.lower().strip()]
    client_order += [
        _order_to_dict(k.client_order, k) for k in AssociatedDoubanOrder.all() if k.contract.lower().strip() == sn.lower().strip()]
    if client_order:
        return jsonify({'ret': True, 'data': client_order[0]})
    elif douban_order:
        return jsonify({'ret': True, 'data': douban_order[0]})
    else:
        return jsonify({'ret': False, 'data': {}})


@api_bp.route('/search/<type>/<id>/order', methods=['GET'])
def search_order(type, id):
    if type == 'client_order':
        client_order = ClientOrder.get(id)
        if client_order:
            return jsonify({'ret':True, 'data':_order_to_dict(client_order)})
        return jsonify({'ret':False, 'data':{}}) 
    elif type == 'douban_order':
        douban_order = DoubanOrder.get(id)
        if douban_order:
            return jsonify({'ret':True, 'data':_order_to_dict(douban_order)})
        return jsonify({'ret':False, 'data':{}})
    elif type == 'ass_douban_order':
        client_order = ClientOrder.get(id)
        if client_order:
            return jsonify({'ret':True, 'data':_order_to_dict(client_order, client_order.associated_douban_orders[0])})
        return jsonify({'ret':False, 'data':{}})
    return jsonify({'ret':False, 'data':{}})
