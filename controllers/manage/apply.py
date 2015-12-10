# -*- coding: utf-8 -*-
import datetime

from flask import Blueprint, request, g, abort
from flask import render_template as tpl

from models.user import TEAM_TYPE_LEADER, TEAM_TYPE_SUPER_LEADER
from models.client_order import ClientOrder, CONTRACT_STATUS_APPLYCONTRACT, CONTRACT_STATUS_DELETEAPPLY, CONTRACT_STATUS_DELETEAGREE
from models.douban_order import DoubanOrder
from models.invoice import Invoice, INVOICE_STATUS_APPLY, MediumInvoicePay, MEDIUM_INVOICE_STATUS_APPLY, MediumRebateInvoice, AgentInvoicePay
from models.outsource import MergerOutSource, MergerDoubanOutSource, MergerPersonalOutSource, MergerDoubanPersonalOutSource, MERGER_OUTSOURCE_STATUS_APPLY

manage_apply_bp = Blueprint(
    'manage_apply', __name__, template_folder='../../templates/manage/apply/')


@manage_apply_bp.route('/order', methods=['GET'])
def order():
    if not (g.user.is_leader() or g.user.is_super_leader()):
        abort(403)
    orders = list(ClientOrder.query.filter_by(
        contract_status=CONTRACT_STATUS_APPLYCONTRACT))
    orders += list(DoubanOrder.query.filter_by(contract_status=CONTRACT_STATUS_APPLYCONTRACT))
    orders = [k for k in orders if k.status == 1]
    if g.user.team.type == TEAM_TYPE_LEADER:
        orders = [o for o in orders if g.user.location in o.locations]
    search_info = request.values.get('search_info', '')
    location = int(request.values.get('location', 0))
    if search_info:
        orders = [k for k in orders if search_info.lower().strip()
                  in k.search_info.lower()]
    if location:
        orders = [k for k in orders if location in k.locations]
    return tpl('/manage/apply/order.html', title=u'合同审批', orders=orders,
               search_info=search_info, location=location, a_type="order")


@manage_apply_bp.route('/order/del', methods=['GET'])
def order_del():
    if not (g.user.is_leader() or g.user.is_super_leader()):
        abort(403)
    orders = list(ClientOrder.query.filter_by(
        contract_status=CONTRACT_STATUS_DELETEAPPLY))
    orders += list(DoubanOrder.query.filter_by(contract_status=CONTRACT_STATUS_DELETEAPPLY))
    orders = [k for k in orders if k.status == 1]
    if g.user.team.type == TEAM_TYPE_LEADER:
        orders = [o for o in orders if g.user.location in o.locations]
    search_info = request.values.get('search_info', '')
    location = int(request.values.get('location', 0))
    if search_info:
        orders = [k for k in orders if search_info.lower().strip()
                  in k.search_info.lower()]
    if location:
        orders = [k for k in orders if location in k.locations]
    return tpl('/manage/apply/order.html', title=u'撤单审批', orders=orders,
               search_info=search_info, location=location, a_type="order")


@manage_apply_bp.route('/order/del_check', methods=['GET'])
def order_del_check():
    if not g.user.is_super_leader():
        abort(403)
    orders = list(ClientOrder.query.filter_by(
        contract_status=CONTRACT_STATUS_DELETEAGREE))
    orders += list(DoubanOrder.query.filter_by(contract_status=CONTRACT_STATUS_DELETEAGREE))
    orders = [k for k in orders if k.status == 1]
    search_info = request.values.get('search_info', '')
    location = int(request.values.get('location', 0))
    if search_info:
        orders = [k for k in orders if search_info.lower().strip()
                  in k.search_info.lower()]
    if location:
        orders = [k for k in orders if location in k.locations]
    return tpl('/manage/apply/order.html', title=u'确认撤单审批', orders=orders,
               search_info=search_info, location=location, a_type="order")


@manage_apply_bp.route('/order/invoice', methods=['GET'])
def invoice():
    if not (g.user.is_leader() or g.user.is_super_leader()):
        abort(403)
    orders = list(set([k.client_order for k in Invoice.query.filter_by(
        invoice_status=INVOICE_STATUS_APPLY)]))
    if g.user.team.type == TEAM_TYPE_LEADER:
        orders = [o for o in orders if g.user.location in o.locations]
    search_info = request.values.get('search_info', '')
    location = int(request.values.get('location', 0))
    if search_info:
        orders = [k for k in orders if search_info.lower().strip()
                  in k.search_info.lower()]
    if location:
        orders = [k for k in orders if location in k.locations]
    return tpl('/manage/apply/order.html', title=u'客户发票审批', orders=orders,
               search_info=search_info, location=location, a_type="invoice")


@manage_apply_bp.route('/order/medium_pay', methods=['GET'])
def medium_pay():
    if not g.user.is_super_leader():
        abort(403)
    orders = list(set([k.client_order for k in MediumInvoicePay.query.filter_by(
        pay_status=MEDIUM_INVOICE_STATUS_APPLY)]))
    search_info = request.values.get('search_info', '')
    location = int(request.values.get('location', 0))
    if search_info:
        orders = [k for k in orders if search_info.lower().strip()
                  in k.search_info.lower()]
    if location:
        orders = [k for k in orders if location in k.locations]
    return tpl('/manage/apply/order.html', title=u'媒体打款审批', orders=orders,
               search_info=search_info, location=location, a_type="medium_pay")


@manage_apply_bp.route('/order/medium_rebate_invoice', methods=['GET'])
def medium_rebate_invoice():
    if not (g.user.is_leader() or g.user.is_super_leader()):
        abort(403)
    orders = list(set([k.client_order for k in MediumRebateInvoice.query.filter_by(
        invoice_status=INVOICE_STATUS_APPLY)]))
    if g.user.team.type == TEAM_TYPE_LEADER:
        orders = [o for o in orders if g.user.location in o.locations]
    search_info = request.values.get('search_info', '')
    location = int(request.values.get('location', 0))
    if search_info:
        orders = [k for k in orders if search_info.lower().strip()
                  in k.search_info.lower()]
    if location:
        orders = [k for k in orders if location in k.locations]
    return tpl('/manage/apply/order.html', title=u'客户发票审批', orders=orders,
               search_info=search_info, location=location, a_type="medium_rebate_invoice")


@manage_apply_bp.route('/order/agent_pay', methods=['GET'])
def agent_pay():
    if not g.user.is_super_leader():
        abort(403)
    orders = list(set([k.client_order for k in AgentInvoicePay.query.filter_by(
        pay_status=MEDIUM_INVOICE_STATUS_APPLY)]))
    search_info = request.values.get('search_info', '')
    location = int(request.values.get('location', 0))
    if search_info:
        orders = [k for k in orders if search_info.lower().strip()
                  in k.search_info.lower()]
    if location:
        orders = [k for k in orders if location in k.locations]
    return tpl('/manage/apply/order.html', title=u'代理返点打款审批', orders=orders,
               search_info=search_info, location=location, a_type="agent_pay")


@manage_apply_bp.route('/order/outsource', methods=['GET'])
def outsource():
    if not (g.user.is_leader() or g.user.is_super_leader()):
        abort(403)
    orders = list(ClientOrder.all())
    orders += list(DoubanOrder.all())
    orders = [k for k in orders if k.status == 1]
    search_info = request.values.get('search_info', '')
    location = int(request.values.get('location', 0))
    if search_info:
        orders = [k for k in orders if search_info.lower().strip()
                  in k.search_info.lower()]
    if location:
        orders = [k for k in orders if location in k.locations]
    if g.user.team.type == TEAM_TYPE_LEADER:
        orders = [
            o for o in orders if g.user.location in o.locations and o.get_outsources_by_status(1)]
    elif g.user.team.type == TEAM_TYPE_SUPER_LEADER:
        orders = [o for o in orders if o.get_outsources_by_status(5)]
    if g.user.is_super_admin():
        orders = [o for o in orders if o.get_outsources_by_status(
            5) or o.get_outsources_by_status(1)]
    return tpl('/manage/apply/order.html', title=u'外包费用报备审批', orders=orders,
               search_info=search_info, location=location, a_type="outsource")


@manage_apply_bp.route('/order/outsource_pay', methods=['GET'])
def outsource_pay():
    if not g.user.is_super_leader():
        abort(403)
    orders = [k for k in MergerOutSource.query.filter_by(
        status=MERGER_OUTSOURCE_STATUS_APPLY)]
    orders += [k for k in MergerDoubanOutSource.query.filter_by(
        status=MERGER_OUTSOURCE_STATUS_APPLY)]
    return tpl('/manage/apply/order.html', title=u'对公外包费用付款审批', orders=orders, a_type="outsource_pay",
               location=0)


@manage_apply_bp.route('/order/outsource_personal_pay', methods=['GET'])
def outsource_personal_pay():
    if not g.user.is_super_leader():
        abort(403)
    orders = [k for k in MergerPersonalOutSource.query.filter_by(
        status=MERGER_OUTSOURCE_STATUS_APPLY)]
    orders += [
        k for k in MergerDoubanPersonalOutSource.query.filter_by(status=MERGER_OUTSOURCE_STATUS_APPLY)]
    return tpl('/manage/apply/order.html', title=u'对个人外包费用付款审批', orders=orders, a_type="outsource_personal_pay",
               location=0)
