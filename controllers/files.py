# -*- coding: UTF-8 -*-
from flask import Blueprint, request, current_app as app, abort, g, url_for, render_template as tpl
from flask import jsonify, send_from_directory, redirect, flash

from models.order import Order
from models.client_order import (ClientOrder, CONTRACT_STATUS_NEW, CONTRACT_STATUS_APPLYREJECT,
                                 CONTRACT_STATUS_MEDIA, CONTRACT_STATUS_APPLYCONTRACT)
from models.framework_order import FrameworkOrder
from models.medium_framework_order import MediumFrameworkOrder
from searchAd.models.framework_order import searchAdFrameworkOrder
from searchAd.models.client import searchAdAgent
from searchAd.models.medium import searchAdMedium
from models.douban_order import DoubanOrder
from models.client_medium_order import ClientMediumOrder
from models.associated_douban_order import AssociatedDoubanOrder
from models.user import User
from libs.files import files_set, attachment_set
from libs.email_signals import zhiqu_contract_apply_signal
from models.attachment import Attachment
from searchAd.models.client_order import searchAdClientOrder
from searchAd.models.order import searchAdOrder
from searchAd.models.rebate_order import searchAdRebateOrder
from models.client import Agent
from models.medium import Medium, MediumGroup


files_bp = Blueprint('files', __name__, template_folder='../templates/files')

FILE_TYPE_CONTRACT = 0
FILE_TYPE_SCHEDULE = 1
FILE_TYPE_OUTSOURCE = 3
FILE_TYPE_OTHERS = 4
FILE_TYPE_AGENT = 9
FILE_TYPE_FINISH = 10
FILE_TYPE_MEDIUM = 12
FILE_TYPE_MEDIUM_GROUP = 13
FILE_TYPE_BILL = 14   # 效果部门结算单


# 客户资质（包括代理和媒体）
FILE_TYPE_LICENCE = 100  # 营业执照
FILE_TYPE_F_CERTIFICATE = 101  # 税务登记证
FILE_TYPE_O_CERTIFICATE = 102  # 组织机构代码证
FILE_TYPE_TAX_CERTIFICATE = 103  # 一般纳税人证明
FILE_TYPE_T_INFO = 104  # 盖章的开票信息


@files_bp.route('/files/<filename>', methods=['GET'])
def files(filename):
    config = app.upload_set_config.get('files')
    if config is None:
        abort(404)
    return send_from_directory(config.destination, filename.encode('utf-8'))


@files_bp.route('/attachment/<filename>', methods=['GET'])
def attachment(filename):
    config = app.upload_set_config.get('attachment')
    if config is None:
        abort(404)
    return send_from_directory(config.destination, filename.encode('utf-8'))


@files_bp.route('/mediums/<filename>', methods=['GET'])
def mediums(filename):
    config = app.upload_set_config.get('mediums')
    if config is None:
        abort(404)
    return send_from_directory(config.destination, filename.encode('utf-8'))


@files_bp.route('/upload', methods=['POST'])
def upload():
    if 'file' in request.files:
        filename = files_set.save(request.files['file'])
        return jsonify({'status': 0, 'filename': filename})
    return jsonify({'status': 1, 'msg': 'file not exits or type not allowed'})


def attachment_upload(order, file_type=FILE_TYPE_CONTRACT):
    if order and 'file' in request.files:
        try:
            request.files['file'].filename.encode('gb2312')
        except:
            flash(u'文件名中包含非正常字符，请使用标准字符', 'danger')
            return redirect("%s" % (order.info_path()))

        if file_type in [FILE_TYPE_AGENT, FILE_TYPE_MEDIUM, FILE_TYPE_MEDIUM_GROUP]:
            filename = files_set.save(request.files['file'])
        else:
            filename = attachment_set.save(request.files['file'])
        if file_type == FILE_TYPE_CONTRACT:
            attachment = order.add_contract_attachment(g.user, filename)
            flash(u'合同文件上传成功!', 'success')
        elif file_type == FILE_TYPE_FINISH:
            attachment = order.add_finish_attachment(g.user, filename)
            flash(u'合同扫描件上传成功!', 'success')
        elif file_type == FILE_TYPE_BILL:
            attachment = order.add_finish_attachment(g.user, filename)
            flash(u'结算单上传成功!', 'success')
        elif file_type == FILE_TYPE_SCHEDULE:
            attachment = order.add_schedule_attachment(g.user, filename)
            flash(u'文件上传成功!', 'success')
        elif file_type == FILE_TYPE_OUTSOURCE:
            flash(u'资料上传成功', 'success')
            order.add_outsource_attachment(g.user, filename)
            return redirect(order.outsource_path())
        elif file_type == FILE_TYPE_AGENT:
            flash(u'资料上传成功', 'success')
            order.add_agent_attachment(g.user, filename)
            return redirect(order.agent_path())
        elif file_type == FILE_TYPE_MEDIUM:
            flash(u'资料上传成功', 'success')
            order.add_medium_attachment(g.user, filename)
            return redirect(order.medium_path())
        elif file_type == FILE_TYPE_MEDIUM_GROUP:
            flash(u'资料上传成功', 'success')
            order.add_medium_group_attachment(g.user, filename)
            return redirect(order.medium_group_path())
        elif file_type == FILE_TYPE_OTHERS:
            flash(u'其他资料上传成功', 'success')
            attachment = order.add_other_attachment(g.user, filename)
        if order.contract_status not in [CONTRACT_STATUS_NEW, CONTRACT_STATUS_APPLYREJECT,
                                         CONTRACT_STATUS_MEDIA, CONTRACT_STATUS_APPLYCONTRACT]:
            contract_email(order, attachment)
    else:
        flash(u'订单不存在，或文件上传出错!', 'danger')
    return redirect("%s#attachment-%s-%s" % (order.info_path(), order.kind, order.id))


@files_bp.route('/client/contract/upload', methods=['POST'])
def client_contract_upload():
    order_id = request.values.get('order')
    order = ClientOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_CONTRACT)


@files_bp.route('/searchAd_client/contract/upload', methods=['POST'])
def searchAd_client_contract_upload():
    order_id = request.values.get('order')
    order = searchAdClientOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_CONTRACT)


@files_bp.route('/attachment/<order_id>/<aid>/delete', methods=['GET'])
def attachment_delete(order_id, aid):
    attachment = Attachment.get(aid)
    target_type = attachment.target_type
    attachment.delete()
    flash(u'删除成功!', 'success')
    if target_type == 'ClientOrder':
        return redirect(url_for("files.client_order_files", order_id=order_id))
    elif target_type == 'Order':
        return redirect(url_for("files.medium_order_files", order_id=order_id))
    elif target_type == 'DoubanOrder':
        return redirect(url_for("files.douban_order_files", order_id=order_id))
    elif target_type == 'AssociatedDoubanOrder':
        return redirect(url_for("files.associated_douban_order_files", order_id=order_id))
    elif target_type == 'FrameworkOrder':
        return redirect(url_for("files.framework_order_files", order_id=order_id))
    elif target_type == 'searchAdFrameworkOrder':
        return redirect(url_for("files.searchAd_framework_order_files", order_id=order_id))
    elif target_type == 'searchAdClientOrder':
        return redirect(url_for("files.searchAd_client_order_files", order_id=order_id))
    elif target_type == 'searchAdOrder':
        return redirect(url_for("files.searchAd_medium_order_files", order_id=order_id))
    elif target_type == 'ClientMediumOrder':
        return redirect(url_for("files.client_meduim_order_files", order_id=order_id))


@files_bp.route('/client/schedule/upload', methods=['POST'])
def client_schedule_upload():
    order_id = request.values.get('order')
    order = ClientOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_SCHEDULE)


@files_bp.route('/searchAd_client/schedule/upload', methods=['POST'])
def searchAd_client_schedule_upload():
    order_id = request.values.get('order')
    order = searchAdClientOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_SCHEDULE)


@files_bp.route('/medium/contract/upload', methods=['POST'])
def medium_contract_upload():
    order_id = request.values.get('order')
    order = Order.get(order_id)
    return attachment_upload(order, FILE_TYPE_CONTRACT)


@files_bp.route('/searchAd_medium/contract/upload', methods=['POST'])
def searchAd_medium_contract_upload():
    order_id = request.values.get('order')
    order = searchAdOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_CONTRACT)


@files_bp.route('/medium/schedule/upload', methods=['POST'])
def medium_schedule_upload():
    order_id = request.values.get('order')
    order = Order.get(order_id)
    return attachment_upload(order, FILE_TYPE_SCHEDULE)


@files_bp.route('/searchAd_medium/schedule/upload', methods=['POST'])
def searchAd_medium_schedule_upload():
    order_id = request.values.get('order')
    order = searchAdOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_SCHEDULE)


@files_bp.route('/framework/contract/upload', methods=['POST'])
def framework_contract_upload():
    order_id = request.values.get('order')
    order = FrameworkOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_CONTRACT)


@files_bp.route('/framework/schedule/upload', methods=['POST'])
def framework_schedule_upload():
    order_id = request.values.get('order')
    order = FrameworkOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_SCHEDULE)


@files_bp.route('/medium_framework/contract/upload', methods=['POST'])
def medium_framework_contract_upload():
    order_id = request.values.get('order')
    order = MediumFrameworkOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_CONTRACT)


@files_bp.route('/medium_framework/schedule/upload', methods=['POST'])
def medium_framework_schedule_upload():
    order_id = request.values.get('order')
    order = MediumFrameworkOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_SCHEDULE)


@files_bp.route('/searchAd_framework/contract/upload', methods=['POST'])
def searchAd_framework_contract_upload():
    order_id = request.values.get('order')
    order = searchAdFrameworkOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_CONTRACT)


@files_bp.route('/searchAd_framework/schedule/upload', methods=['POST'])
def searchAd_framework_schedule_upload():
    order_id = request.values.get('order')
    order = searchAdFrameworkOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_SCHEDULE)


@files_bp.route('/searchAd_framework/others/upload', methods=['POST'])
def searchAd_framework_others_upload():
    order_id = request.values.get('order')
    order = searchAdFrameworkOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_OTHERS)


@files_bp.route('/searchAd_rebate/contract/upload', methods=['POST'])
def searchAd_rebate_contract_upload():
    order_id = request.values.get('order')
    order = searchAdRebateOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_CONTRACT)


@files_bp.route('/searchAd_rebate/schedule/upload', methods=['POST'])
def searchAd_rebate_schedule_upload():
    order_id = request.values.get('order')
    order = searchAdRebateOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_SCHEDULE)


@files_bp.route('/framework/others/upload', methods=['POST'])
def framework_others_upload():
    order_id = request.values.get('order')
    order = FrameworkOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_OTHERS)


@files_bp.route('/client/others/upload', methods=['POST'])
def client_others_upload():
    order_id = request.values.get('order')
    order = ClientOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_OTHERS)


@files_bp.route('/douban/others/upload', methods=['POST'])
def douban_others_upload():
    order_id = request.values.get('order')
    order = DoubanOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_OTHERS)


@files_bp.route('/medium_framework/others/upload', methods=['POST'])
def medium_framework_others_upload():
    order_id = request.values.get('order')
    order = MediumFrameworkOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_OTHERS)


@files_bp.route('/douban/contract/upload', methods=['POST'])
def douban_contract_upload():
    order_id = request.values.get('order')
    order = DoubanOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_CONTRACT)


@files_bp.route('/douban/schedule/upload', methods=['POST'])
def douban_schedule_upload():
    order_id = request.values.get('order')
    order = DoubanOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_SCHEDULE)


@files_bp.route('/associated_douban/contract/upload', methods=['POST'])
def associated_douban_contract_upload():
    order_id = request.values.get('order')
    order = AssociatedDoubanOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_CONTRACT)


@files_bp.route('/associated_douban/schedule/upload', methods=['POST'])
def associated_douban_schedule_upload():
    order_id = request.values.get('order')
    order = AssociatedDoubanOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_SCHEDULE)


@files_bp.route('/outsource/client_order/upload', methods=['POST'])
def outsource_client_order_upload():
    order_id = request.values.get('order')
    order = ClientOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_OUTSOURCE)


@files_bp.route('/client/agent/upload', methods=['POST'])
def client_agent_upload():
    agent_id = request.values.get('agent')
    agent = Agent.get(agent_id)
    return attachment_upload(agent, FILE_TYPE_AGENT)


@files_bp.route('/searchAd_client/agent/upload', methods=['POST'])
def searchAd_client_agent_upload():
    agent_id = request.values.get('agent')
    agent = searchAdAgent.get(agent_id)
    return attachment_upload(agent, FILE_TYPE_AGENT)


@files_bp.route('/outsource/douban_order/upload', methods=['POST'])
def outsource_douban_order_upload():
    order_id = request.values.get('order')
    order = DoubanOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_OUTSOURCE)


@files_bp.route('/client_order/<order_id>/all_files', methods=['get'])
def client_order_files(order_id):
    co = ClientOrder.get(order_id)
    return tpl("order_files.html", order=co)


@files_bp.route('/medium_order/<order_id>/all_files', methods=['get'])
def medium_order_files(order_id):
    co = Order.get(order_id)
    return tpl("order_files.html", order=co)


@files_bp.route('/searchAd_client_order/<order_id>/all_files', methods=['GET'])
def searchAd_client_order_files(order_id):
    order = searchAdClientOrder.get(order_id)
    return tpl("search_order_files.html", order=order)


@files_bp.route('/searchAd_medium_order/<order_id>/all_files', methods=['get'])
def searchAd_medium_order_files(order_id):
    order = searchAdOrder.get(order_id)
    return tpl('search_order_files.html', order=order)


@files_bp.route('/framework_order/<order_id>/all_files', methods=['get'])
def framework_order_files(order_id):
    fo = FrameworkOrder.get(order_id)
    return tpl("order_files.html", order=fo)


@files_bp.route('/medium_framework_order/<order_id>/all_files', methods=['get'])
def medium_framework_order_files(order_id):
    fo = MediumFrameworkOrder.get(order_id)
    return tpl("order_files.html", order=fo)


@files_bp.route('/searchAdframework_order/<order_id>/all_files', methods=['get'])
def searchAd_framework_order_files(order_id):
    fo = searchAdFrameworkOrder.get(order_id)
    return tpl("search_order_files.html", order=fo)


@files_bp.route('/douban_order/<order_id>/all_files', methods=['get'])
def douban_order_files(order_id):
    fo = DoubanOrder.get(order_id)
    return tpl("order_files.html", order=fo)


@files_bp.route('/rebate_order/<order_id>/all_files', methods=['get'])
def rebate_order_files(order_id):
    fo = searchAdRebateOrder.get(order_id)
    return tpl("order_files.html", order=fo)


@files_bp.route('/associated_douban_order/<order_id>/all_files', methods=['get'])
def associated_douban_order_files(order_id):
    fo = AssociatedDoubanOrder.get(order_id)
    return tpl("order_files.html", order=fo)


def contract_email(order, attachment):
    if order.__tablename__ == 'bra_searchAd_framework_order':
        to_users = set(User.contracts() +
                       User.medias() +
                       order.sales +
                       [order.creator, g.user])
    elif order.__tablename__ == 'searchAd_bra_client_order':
        to_users = set(User.contracts() +
                       User.medias() +
                       order.agent_sales +
                       order.direct_sales +
                       [order.creator, g.user])
    elif order.__tablename__ == 'bra_framework_order':
        to_users = set(User.contracts() +
                       order.agent_sales +
                       order.direct_sales +
                       [order.creator, g.user])
    elif order.__tablename__ == 'bra_medium_framework_order':
        to_users = set(User.contracts() +
                       order.medium_users +
                       [order.creator, g.user])
    elif order.__tablename__ == 'bra_client_medium_order':
        to_users = set(User.contracts() +
                       User.medias() +
                       order.agent_sales +
                       order.direct_sales +
                       [order.creator, g.user])
    else:
        to_users = set(User.contracts() +
                       User.medias() +
                       order.direct_sales +
                       order.agent_sales +
                       order.operaters +
                       [order.creator, g.user])

    action_msg = u"%s文件更新" % (attachment.type_cn)
    msg = u"""
    文件名:%s
    状态:%s
    上传者:%s""" % (attachment.filename, attachment.status_cn, g.user.name)
    context = {'order': order,
               'sender': g.user,
               'action_msg': action_msg,
               'info': msg,
               'to_users': to_users}
    zhiqu_contract_apply_signal.send(app._get_current_object(), context=context)


@files_bp.route('/finish/client_order/upload', methods=['POST'])
def finish_client_order_upload():
    order_id = request.values.get('order')
    order = ClientOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_FINISH)


@files_bp.route('/finish/douban_order/upload', methods=['POST'])
def finish_douban_order_upload():
    order_id = request.values.get('order')
    order = DoubanOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_FINISH)


@files_bp.route('/finish/framework_order/upload', methods=['POST'])
def finish_framework_order_upload():
    order_id = request.values.get('order')
    order = FrameworkOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_FINISH)


@files_bp.route('/finish/medium_framework_order/upload', methods=['POST'])
def finish_medium_framework_order_upload():
    order_id = request.values.get('order')
    order = MediumFrameworkOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_FINISH)


@files_bp.route('/finish/medium_order/upload', methods=['POST'])
def finish_medium_order_upload():
    order_id = request.values.get('order')
    order = Order.get(order_id)
    return attachment_upload(order, FILE_TYPE_FINISH)


@files_bp.route('/finish/associated_douban/upload', methods=['POST'])
def finish_associated_douban_upload():
    order_id = request.values.get('order')
    order = AssociatedDoubanOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_FINISH)


@files_bp.route('/finish/searchAd_client_order/upload', methods=['POST'])
def finish_searchAd_client_order_upload():
    order_id = request.values.get('order')
    order = searchAdClientOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_FINISH)


@files_bp.route('/bill/searchAd_client_order/upload', methods=['POST'])
def bill_searchAd_client_order_upload():
    order_id = request.values.get('order')
    order = searchAdClientOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_BILL)


@files_bp.route('/finish/searchAd_rebate_order/upload', methods=['POST'])
def finish_searchAd_rebate_order_upload():
    order_id = request.values.get('order')
    order = searchAdRebateOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_FINISH)


@files_bp.route('/finish/searchAd_framework_order/upload', methods=['POST'])
def finish_searchAd_framework_order_upload():
    order_id = request.values.get('order')
    order = searchAdFrameworkOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_FINISH)


@files_bp.route('/finish/searchAd_medium_order/upload', methods=['POST'])
def finish_searchAd_medium_order_upload():
    order_id = request.values.get('order')
    order = searchAdOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_FINISH)


@files_bp.route('/client_medium/contract/upload', methods=['POST'])
def client_medium_order_contract_upload():
    order_id = request.values.get('order')
    order = ClientMediumOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_CONTRACT)


@files_bp.route('/client_medium/schedule/upload', methods=['POST'])
def client_medium_order_schedule_upload():
    order_id = request.values.get('order')
    order = ClientMediumOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_SCHEDULE)


@files_bp.route('/finish/client_medium/upload', methods=['POST'])
def finish_client_medium_order_upload():
    order_id = request.values.get('order')
    order = ClientMediumOrder.get(order_id)
    return attachment_upload(order, FILE_TYPE_FINISH)


@files_bp.route('/client_medium_order/<order_id>/all_files', methods=['get'])
def client_medium_order_files(order_id):
    co = ClientMediumOrder.get(order_id)
    return tpl("order_files.html", order=co)


@files_bp.route('/client/medium/upload', methods=['POST'])
def client_medium_upload():
    medium_id = request.values.get('medium')
    medium = Medium.get(medium_id)
    return attachment_upload(medium, FILE_TYPE_MEDIUM)


@files_bp.route('/searchAd_client/medium/upload', methods=['POST'])
def searchAd_client_medium_upload():
    medium_id = request.values.get('medium')
    medium = searchAdMedium.get(medium_id)
    return attachment_upload(medium, FILE_TYPE_MEDIUM)


@files_bp.route('/client/medium_group/upload', methods=['POST'])
def client_medium_group_upload():
    medium_id = request.values.get('medium')
    medium_group = MediumGroup.get(medium_id)
    return attachment_upload(medium_group, FILE_TYPE_MEDIUM_GROUP)
