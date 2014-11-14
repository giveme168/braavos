# -*- coding: utf-8 -*-
import StringIO
import mimetypes
from werkzeug.datastructures import Headers
from datetime import datetime, timedelta

from flask import Blueprint, request, redirect, abort, url_for, g, Response
from flask import render_template as tpl, json, jsonify, flash

from forms.order import OrderForm
from forms.item import ItemForm

from models.client import Client, Agent
from models.medium import Medium, AdPosition
from models.item import (AdItem, AdSchedule, SALE_TYPE_CN, ITEM_STATUS_NEW,
                         ITEM_STATUS_ACTION_CN, ChangeStateApply, ITEM_STATUS_ARCHIVE,
                         ITEM_STATUS_LEADER_ACTIONS,
                         ITEM_STATUS_ACTION_PRE_ORDER,
                         ITEM_STATUS_ACTION_ORDER_APPLY)
from models.order import Order
from models.user import User, TEAM_TYPE_LEADER
from models.consts import DATE_FORMAT, TIME_FORMAT
from models.excel import Excel
from models.material import Material

from libs.signals import order_apply_signal, reply_apply_signal

order_bp = Blueprint('order', __name__, template_folder='../templates/order')


STATUS_APPLLY = (ITEM_STATUS_ACTION_PRE_ORDER, ITEM_STATUS_ACTION_ORDER_APPLY)


@order_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('order.orders'))


@order_bp.route('/new_order', methods=['GET', 'POST'])
def new_order():
    form = OrderForm(request.form)
    if request.method == 'POST' and form.validate():
        order = Order.add(client=Client.get(form.client.data), campaign=form.campaign.data,
                          medium=Medium.get(form.medium.data), order_type=form.order_type.data,
                          contract=form.contract.data, money=form.money.data,
                          agent=Agent.get(form.agent.data), direct_sales=User.gets(form.direct_sales.data),
                          agent_sales=User.gets(form.agent_sales.data), operaters=User.gets(form.operaters.data),
                          planers=User.gets(form.planers.data), designers=User.gets(form.designers.data),
                          creator=g.user, discount=form.discount.data, create_time=datetime.now())
        flash(u'新建订单成功!', 'success')
        return redirect(url_for("order.order_detail", order_id=order.id, step=0))
    else:
        form.creator.data = g.user.name
    form.order_type.hidden = True
    return tpl('new_order.html', form=form)


@order_bp.route('/order/<order_id>/<step>/', methods=['GET', 'POST'])
def order_detail(order_id, step):
    order = Order.get(order_id)
    if not order:
        abort(404)
    form = OrderForm(request.form)
    leaders = [(m.id, m.name) for m in User.gets_by_team_type(TEAM_TYPE_LEADER)]
    if request.method == 'POST':
        if not order.can_admin(g.user):
            flash(u'您没有编辑权限! 请联系该订单的创建者或者销售同事!', 'danger')
        elif form.validate():
            order.client = Client.get(form.client.data)
            order.campaign = form.campaign.data
            order.medium = Medium.get(form.medium.data)
            order.order_type = form.order_type.data
            order.contract = form.contract.data
            order.money = form.money.data
            order.agent = Agent.get(form.agent.data)
            order.direct_sales = User.gets(form.direct_sales.data)
            order.agent_sales = User.gets(form.agent_sales.data)
            order.operaters = User.gets(form.operaters.data)
            order.designers = User.gets(form.designers.data)
            order.planers = User.gets(form.planers.data)
            order.discount = form.discount.data
            order.save()
            flash(u'订单信息保存成功!', 'success')
    else:
        form.client.data = order.client.id
        form.campaign.data = order.campaign
        if not g.user.is_admin():
            form.medium.choices = [(order.medium.id, order.medium.name)]
        form.medium.data = order.medium.id
        form.order_type.data = order.order_type
        form.contract.data = order.contract
        form.money.data = order.money
        form.agent.data = order.agent.id
        form.direct_sales.data = [u.id for u in order.direct_sales]
        form.agent_sales.data = [u.id for u in order.agent_sales]
        form.operaters.data = [u.id for u in order.operaters]
        form.designers.data = [u.id for u in order.designers]
        form.planers.data = [u.id for u in order.planers]
        form.discount.data = order.discount
        form.creator.data = order.creator.name
    form.order_type.hidden = True
    context = {'form': form,
               'leaders': leaders,
               'order': order,
               'step': step,
               'SALE_TYPE_CN': SALE_TYPE_CN
               }
    return tpl('order.html', **context)


@order_bp.route('/orders', methods=['GET'])
def orders():
    orders = [o for o in Order.all()]
    return display_orders(orders, u'订单列表')


@order_bp.route('/my_orders', methods=['GET'])
def my_orders():
    orders = Order.get_order_by_user(g.user)
    return display_orders(orders, u'我的订单列表')


@order_bp.route('/per_orders', methods=['GET'])
def per_orders():
    orders = Order.all_per_order()
    return display_orders(orders, u'预下单订单列表')


def display_orders(orders, title):
    sortby = request.args.get('sortby', '')
    orderby = request.args.get('orderby', '')
    search_info = request.args.get('searchinfo', '')
    medium_id = int(request.args.get('selected_medium', 0))
    reverse = orderby != 'asc'
    if medium_id:
        orders = [o for o in orders if medium_id == o.medium.id]
    if search_info != '':
        orders = [o for o in orders if search_info in o.name]
    if sortby and len(orders) and hasattr(orders[0], sortby):
        orders = sorted(orders, key=lambda x: getattr(x, sortby), reverse=reverse)
    select_medium = [(m.id, m.name) for m in Medium.all()]
    select_medium.insert(0, (0, u'全部媒体'))
    return tpl('orders.html', orders=orders, medium=select_medium, medium_id=medium_id,
               sortby=sortby, orderby=orderby, search_info=search_info)


@order_bp.route('/items', methods=['GET'])
def items():
    items = AdItem.all()
    return tpl('items.html', items=items)


@order_bp.route('/materials', methods=['GET'])
def materials():
    materials = Material.all()
    return tpl('materials.html', materials=materials)


@order_bp.route('/order/<order_id>/new_item/<type>')
def new_item(order_id, type):
    order = Order.get(order_id)
    if not order:
        abort(404)
    if not order.can_admin(g.user):
        flash(u'您没有创建排期的权限, 请联系订单创建者和销售同事!', 'danger')
        return redirect(url_for('order.order_detail', order_id=order.id, step=0))
    start_date = datetime.today()
    end_date = start_date + timedelta(days=30)
    positions = [(x.id, x.display_name) for x in order.medium.positions]
    return tpl('new_item.html', order=order, positions=positions,
               start_date=start_date, end_date=end_date, type=type,
               SALE_TYPE_CN=SALE_TYPE_CN, SPECIAL_SALE_CN={0: u"否", 1: u"是"})


def check_schedules_post(data):
    """检查排期数据是否合法"""
    try:
        items = json.loads(data)
    except ValueError:
        return '1', "JSON数据格式出错啦"
    else:
        status = 0
        msg = ''
        for item in items:
            position = AdPosition.get(item['position'])
            for (date_str, num_str) in item['schedule'].items():
                _date = datetime.strptime(date_str, DATE_FORMAT).date()
                num = int(num_str)
                if position.can_order_num(_date) < num:
                    status = 1
                    msg += u'%s 最多只能预订 %s \n' % (position.display_name, position.can_order_num(_date))
    return status, msg


def add_schedules(order, data):
    """新增订单项, 排期项"""
    items = json.loads(data)
    for item in items:
        position = AdPosition.get(item['position'])
        ad_item = AdItem.add(order=order, sale_type=item['sale_type'], special_sale=item['special_sale'],
                             position=position, creator=g.user, create_time=datetime.now())
        ad_item.price = position.price
        ad_item.description = item['description']
        ad_item.item_status = ITEM_STATUS_NEW
        ad_item.save()
        for (date_str, num_str) in item['schedule'].items():
            _date = datetime.strptime(date_str, DATE_FORMAT).date()
            num = int(num_str)
            AdSchedule.add(item=ad_item, num=num, date=_date)


@order_bp.route('/order/<order_id>/schedules_post/', methods=["POST"])
def schedules_post(order_id):
    """AJAX 提交排期数据"""
    order = Order.get(order_id)
    if not order:
        abort(404)
    data = request.values.get('data')
    status, msg = check_schedules_post(data)
    if not status:
        add_schedules(order, data)
        flash(u'排期提交成功!', 'success')
    return jsonify({'status': status, 'msg': msg})


@order_bp.route('/schedule_info/', methods=['GET'])
def schedule_info():
    """ajax 获取排期数据"""
    start_date = datetime.strptime(request.values.get('start'), DATE_FORMAT).date()
    end_date = datetime.strptime(request.values.get('end'), DATE_FORMAT).date()
    position = AdPosition.get(request.values.get('position'))
    return jsonify(position.get_schedule(start_date, end_date))


@order_bp.route('/position_list', methods=['GET'])
def position_list():
    # order = Order.get(request.values.get('order'))
    # sale_type = request.values.get('sale_type')
    # special_sale = request.values.get('special_sale')
    return jsonify([(p.id, p.display_name) for p in AdPosition.all()])


@order_bp.route('/item/<item_id>', methods=["GET", "POST"])
def item_detail(item_id):
    item = AdItem.get(item_id)
    if not item:
        abort(404)
    form = ItemForm(request.form)
    if request.method == 'POST' and form.validate():
        item.sale_type = form.sale_type.data
        item.special_sale = form.special_sale.data
        item.description = form.description.data
        item.ad_type = form.ad_type.data
        item.price = form.price.data
        item.priority = form.priority.data
        item.speed = form.speed.data
        item.item_status = form.item_status.data
        item.status = form.status.data
        item.save()
        flash(u'保存成功!', 'success')
    else:
        form.order.data = item.order.name
        form.sale_type.data = item.sale_type
        form.special_sale.data = item.special_sale
        form.position.data = item.position.name
        form.description.data = item.description
        form.ad_type.data = item.ad_type
        form.price.data = item.price
        form.priority.data = item.priority
        form.speed.data = item.speed
        form.item_status.data = item.item_status
        form.status.data = item.status
        form.creator.data = item.creator.name

        form.order.readonly = True
        form.position.readonly = True
        form.creator.readonly = True
    if not g.user.is_admin():
        form.disable_all()
    return tpl('item.html', form=form, item=item)


@order_bp.route('/item/<item_id>/schedule_simple_update', methods=["POST"])
def schedule_simple_update(item_id):
    item = AdItem.get(item_id)
    if not item:
        return jsonify({'msg': u"出错啦, 排期不存在"})
    data = request.values.get('data')
    msg = ""
    status = 0
    schedules_info = json.loads(data)
    flag = False
    for date_str, num in schedules_info.items():
        _date = datetime.strptime(date_str, DATE_FORMAT).date()
        if not item.position.check_order_num(_date, num):
            msg = date_str + u"预订量超过最大可预订量"
            status = 1
    if not status:
        for date_str, num in schedules_info.items():
            _date = datetime.strptime(date_str, DATE_FORMAT).date()
            _schedule = item.schedule_by_date(_date)
            if _schedule:
                if num == 0:
                    flag = True
                    _schedule.delete()
                else:
                    if _schedule.num != num:
                        _schedule.num = num
                        flag = True
                        _schedule.save()
            elif num != 0:
                flag = True
                _schedule = AdSchedule.add(item, num, _date)
        if flag:
            if item.schedule_sum:
                item.change_to_previous_status()
                msg = u"排期修改成功!当前状态回退至上一状态!"
                if item.item_status == ITEM_STATUS_NEW:
                    msg = u'排期更改成功!预下单状态不变更!'
            else:
                item.item_status = ITEM_STATUS_ARCHIVE
                msg = u"当前订单项所有排期总量为0,自动归档!"
        else:
            msg = u"当前订单项排期未做修改"
    return jsonify({'msg': msg, 'status': status})


@order_bp.route('/schedule/<schedule_id>/update', methods=["POST"])
def schedule_update(schedule_id):
    schedule = AdSchedule.get(schedule_id)
    if not schedule:
        abort(404)
    schedule.date = datetime.strptime(request.form.get('date'), DATE_FORMAT).date()
    schedule.start = datetime.strptime(request.form.get('start'), TIME_FORMAT).time()
    schedule.end = datetime.strptime(request.form.get('end'), TIME_FORMAT).time()
    schedule.num = request.form.get('num')
    schedule.save()
    flash(u'投放安排保存成功!', 'success')
    return redirect(url_for("order.item_detail", item_id=schedule.item.id))


@order_bp.route('/schedule/<schedule_id>/delete')
def schedule_delete(schedule_id):
    schedule = AdSchedule.get(schedule_id)
    if not schedule:
        abort(404)
    item = schedule.item
    schedule.delete()
    flash(u'删除成功!', 'success')
    return redirect(url_for("order.item_detail", item_id=item.id))


@order_bp.route('/order/<order_id>/items/update/<step>', methods=['POST'])
def items_status_update(order_id, step):
    order = Order.get(order_id)
    if not order:
        abort(404)
    item_ids = request.form.getlist('item_id')
    leaders = request.form.getlist('leader')
    if not item_ids:
        flash(u"请选择订单项")
    else:
        action = int(request.form.get('action'))
        if action in STATUS_APPLLY:
            if not leaders:
                flash(u"请选择Leader")
                return redirect(url_for('order.order_detail', order_id=order.id, step=step))
            else:
                apply = ChangeStateApply(
                    step,
                    action,
                    [User.get(m).email for m in leaders],
                    order)
                order_apply_signal.send(apply)
                flash(u"请在2个自然日内与审核Leaer联系")
        if action in ITEM_STATUS_LEADER_ACTIONS:
            apply = ChangeStateApply(
                step,
                action,
                [order.creator.email],
                order)
            reply_apply_signal.send(apply)
        items = AdItem.gets(item_ids)
        AdItem.update_items_with_action(items, action, g.user)
        msg = '\n\n'.join(['%s : %s' % (item.name, ITEM_STATUS_ACTION_CN[action]) for item in items])
        order.add_comment(g.user, msg)
        flash(u'%s个排期项%s。请将理由在留言板上留言说明' % (len(items), ITEM_STATUS_ACTION_CN[action]))
        step = AdItem.get_next_step(step, action)
    return redirect(url_for('order.order_detail', order_id=order.id, step=step))


@order_bp.route('/schedule_file/<order_id>', methods=['GET', 'POST'])
def export_schedule(order_id):
    order = Order.get(order_id)
    filename = ("%s-%s.xls" % (order.name, datetime.now().strftime('%Y%m%d%H%M%S'))).encode('utf-8')
    xls = Excel().write_excle(order.excel_table)
    response = get_download_response(xls, filename)
    return response


def get_download_response(xls, filename):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    xls.save(output)
    response.data = output.getvalue()
    mimetype_tuple = mimetypes.guess_type(filename)
    response_headers = Headers({
        'Pragma': "public",
        'Expires': '0',
        'Cache-Control': 'must-revalidate, post-check=0, pre-check=0',
        'Cache-Control': 'private',
        'Content-Type': mimetype_tuple[0],
        'Content-Disposition': 'attachment; filename=\"%s\";' % filename,
        'Content-Transfer-Encoding': 'binary',
        'Content-Length': len(response.data)
    })
    response.headers = response_headers
    response.set_cookie('fileDownload', 'true', path='/')
    return response
