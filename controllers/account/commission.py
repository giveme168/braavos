# -*- coding: utf-8 -*-
import datetime
import calendar as cal
import operator

from flask import Blueprint, request, redirect, url_for, g, abort, jsonify
from flask import render_template as tpl, flash

from models.user import User, TEAM_LOCATION_HUABEI, TEAM_LOCATION_HUADONG, TEAM_LOCATION_HUANAN
from models.account.saler import Commission
from models.client_order import BackMoney, BackInvoiceRebate
from models.douban_order import BackMoney as DoubanBackMoney
from models.douban_order import BackInvoiceRebate as DoubanBackInvoiceRebate
from models.outsource import DoubanOutSource, OutSource
from libs.date_helpers import (
    check_Q_get_monthes, check_month_get_Q, get_monthes_pre_days)
from controllers.account.helpers.commission_helpers import write_report_excel


account_commission_bp = Blueprint(
    'account_commission', __name__, template_folder='../../templates/account/commission/')


@account_commission_bp.route('/', methods=['GET'])
def index():
    if not (g.user.is_super_leader() or g.user.is_finance()):
        return abort(404)
    if g.user.is_searchad_member() and (not g.user.is_admin()) and (not g.user.is_super_leader()):
        users = [u for u in User.all() if u.is_search_saler]
    else:
        users = [u for u in User.all() if u.is_out_saler]
    huabei_users = [u for u in users if u.location == TEAM_LOCATION_HUABEI]
    huadong_users = [u for u in users if u.location == TEAM_LOCATION_HUADONG]
    huanan_users = [u for u in users if u.location == TEAM_LOCATION_HUANAN]
    return tpl('/account/commission/index.html', huabei_users=huabei_users,
               huadong_users=huadong_users, huanan_users=huanan_users)


@account_commission_bp.route('/<user_id>/info', methods=['GET'])
def info(user_id):
    if not (g.user.is_super_leader() or g.user.is_finance()):
        return abort(404)
    user = User.get(user_id)
    comms = Commission.query.filter_by(user_id=user_id)
    return tpl('/account/commission/info.html', user=user, comms=comms)


@account_commission_bp.route('/<user_id>/create', methods=['GET', 'POST'])
def create(user_id):
    if not (g.user.is_super_leader() or g.user.is_finance()):
        return abort(404)
    user = User.get(user_id)
    if request.method == 'POST':
        rate = float(request.values.get('rate', 0))
        year = int(request.values.get('year', datetime.datetime.now().year))
        try:
            commission = Commission.add(
                user=user,
                creator=g.user,
                rate=rate,
                year=year)
            if commission:
                flash(u'添加提成信息成功', 'success')
                return redirect(url_for('account_commission.info', user_id=user_id))
            else:
                flash(u'该年度已存在返点信息', 'danger')
                return redirect(url_for('account_commission.create', user_id=user_id))
        except:
            flash(u'该年度已存在返点信息', 'danger')
    return tpl('/account/commission/create.html', user=user)


@account_commission_bp.route('/<user_id>/<mid>/update', methods=['GET', 'POST'])
def update(user_id, mid):
    if not (g.user.is_super_leader() or g.user.is_finance()):
        return abort(404)
    commission = Commission.get(mid)
    if request.method == 'POST':
        rate = float(request.values.get('rate', 0))
        year = int(request.values.get('year', datetime.datetime.now().year))
        try:
            commission.year = year
            commission.rate = rate
            commission.save()
            flash(u'修改提成信息成功', 'success')
            return redirect(url_for('account_commission.info', user_id=user_id))
        except:
            flash(u'该年度已存在返点信息', 'danger')
            return redirect(url_for('account_commission.update', user_id=user_id, mid=mid))
    return tpl('/account/commission/update.html', commission=commission)


@account_commission_bp.route('/<user_id>/<mid>/delete', methods=['GET'])
def delete(user_id, mid):
    if not (g.user.is_super_leader() or g.user.is_finance()):
        return abort(404)
    commission = Commission.get(mid)
    commission.delete()
    return jsonify({'id': mid})


# 账期区间, 根据账期获取账期提成比例
def _back_day_rate(day):
    day_rate = {}
    # 0-30天返点120
    for k in range(-100, 31):
        day_rate[k] = 1.2
    for k in range(31, 61):
        day_rate[k] = 1.1
    for k in range(61, 91):
        day_rate[k] = 1
    for k in range(91, 101):
        day_rate[k] = 0.98
    for k in range(101, 121):
        day_rate[k] = 0.96
    for k in range(121, 151):
        day_rate[k] = 0.94
    for k in range(151, 181):
        day_rate[k] = 0.92
    for k in range(181, 361):
        day_rate[k] = 0.9
    if day in day_rate:
        return day_rate[day]
    return 0.5


# 根据摸个合同获取最后一次回款时间，及当季度总回款金额
def _order_back_money_by_Q(order_id, start_Q_month, back_moneys, now_Q_back_moneys):
    now_Q_back_money_obj = [
        k for k in now_Q_back_moneys if k['order_id'] == order_id]
    now_Q_back_moneys = sum([k['money'] for k in now_Q_back_money_obj])
    now_Q_back_money_obj = sorted(
        now_Q_back_money_obj, key=operator.itemgetter('back_time'), reverse=True)
    if now_Q_back_money_obj:
        now_Q_back_money_last_time = now_Q_back_money_obj[
            0]['back_time'].strftime('%Y-%m-%d')
    else:
        now_Q_back_money_last_time = u'无'
    # 获取本季度之前的所有回款
    before_Q_back_money_obj = [k for k in now_Q_back_money_obj if k[
        'order_id'] == order_id and k['back_time'] < start_Q_month]
    before_Q_back_moneys = sum([k.money for k in before_Q_back_money_obj])

    return {'last_time': now_Q_back_money_last_time,
            'now_Q_back_moneys': now_Q_back_moneys,
            'before_Q_back_moneys': before_Q_back_moneys}


# 计算某个合同执行额
def _order_executive_reports(money, start, end):
    if money:
        pre_money = float(money) / ((start - start).days + 1)
    else:
        pre_money = 0
    pre_month_days = get_monthes_pre_days(datetime.datetime.strptime(start.strftime('%Y-%m-%d'), '%Y-%m-%d'),
                                          datetime.datetime.strptime(end.strftime('%Y-%m-%d'), '%Y-%m-%d'))
    pre_month_money_data = []
    for k in pre_month_days:
        pre_month_money_data.append(
            {'money': pre_money * k['days'], 'month_day': k['month'], 'days': k['days']})
    return pre_month_money_data


# 计算某个合同中每个月的回款数，该合同所属回款季度
def _belong_time_by_back_money(money, start, end, back_money_obj):
    # 获取合同执行额
    report_money = _order_executive_reports(money, start, end)
    now_Q_back_moneys = back_money_obj['now_Q_back_moneys']
    t_report_money = 0
    report_times = []
    # 根据回款向前归并，比如合同执行时间跨月，回款要一次评分在三个月
    for k in range(len(report_money)):
        t_report_money += report_money[k]['money']
        if now_Q_back_moneys <= 0:
            break
        if report_money[k]['money'] < now_Q_back_moneys:
            report_times.append((report_money[k]['month_day'], report_money[k]['money']))
        else:
            report_times.append((report_money[k]['month_day'], now_Q_back_moneys))
        now_Q_back_moneys -= report_money[k]['money']
    # 确定回款属于哪个执行月
    if report_times:
        if len(report_times) > 1:
            start = report_times[0][0].strftime(
                '%Y') + '.' + check_month_get_Q(report_times[0][0].strftime('%m'))
            end = report_times[-1][0].strftime('%Y') + '.' + check_month_get_Q(
                report_times[-1][0].strftime('%m'))
            if start == end:
                return {'back_moneys': report_times, 'belong_time': end}
            return {'back_moneys': report_times, 'belong_time': start + u' 至 ' + end}
        start = report_times[0][0].strftime(
            '%Y') + '.' + check_month_get_Q(report_times[0][0].strftime('%m'))
        return {'back_moneys': report_times, 'belong_time': start}
    return {'back_moneys': [], 'belong_time': u'无'}


def _all_outsource():
    outsource = [{'order_id': o.douban_order.id, 'money': o.num, 'type': 'douban'}
                 for o in DoubanOutSource.all() if o.status in [2, 3, 4]]
    outsource += [{'order_id': o.medium_order.client_order.id, 'money': o.num, 'type': 'client'}
                  for o in OutSource.all() if o.status in [2, 3, 4]]
    return outsource


def _order_back_money_data(order, start_Q_month, end_Q_month, back_moneys):
    order_back_moneys = [k for k in back_moneys if k['order_id'] == order.id]
    order_back_moneys = sorted(
        order_back_moneys, key=operator.itemgetter('back_time'), reverse=True)
    # 获取合同每月的执行金额，用于计算回款属于哪个执行月
    money = order.money
    start = order.client_start
    end = order.client_end
    if money:
        pre_money = float(money) / ((end - start).days + 1)
    else:
        pre_money = 0
    pre_month_days = get_monthes_pre_days(datetime.datetime.strptime(start.strftime('%Y-%m-%d'), '%Y-%m-%d'),
                                          datetime.datetime.strptime(end.strftime('%Y-%m-%d'), '%Y-%m-%d'))
    total_back_money = money
    for k in range(len(pre_month_days)):
        # 累计执行额
        month_money = pre_money * pre_month_days[k]['days']
        for b in range(len(order_back_moneys)):
            back_money = order_back_moneys[b]['money']
            if 'belong_time' not in order_back_moneys[b]:
                if month_money - back_money > 0.0:
                    order_back_moneys[b][
                        'belong_time'] = pre_month_days[k]['month']
                    month_money -= back_money
                    total_back_money -= back_money
                elif month_money - back_money < 0.0:
                    order_back_moneys[b]['money'] = month_money
                    order_back_moneys[b][
                        'belong_time'] = pre_month_days[k]['month']
                    total_back_money -= month_money
                    # 当回款金额大于当月执行额是，要把回款进行拆分，归属到下个执行月
                    if b != len(order_back_moneys) - 1:
                        db = {}
                        db['type'] = order_back_moneys[b]['type']
                        db['money'] = back_money - month_money
                        db['back_time'] = order_back_moneys[b]['back_time']
                        db['order'] = order_back_moneys[b]['order']
                        db['order_id'] = order_back_moneys[b]['order_id']
                        order_back_moneys.insert(b + 1, db)
                        month_money = 0.0
                        continue
                    else:
                        db = {}
                        db['type'] = order_back_moneys[b]['type']
                        db['money'] = back_money - month_money
                        db['back_time'] = order_back_moneys[b]['back_time']
                        db['order'] = order_back_moneys[b]['order']
                        db['order_id'] = order_back_moneys[b]['order_id']
                        if k == len(pre_month_days) - 1:
                            db['belong_time'] = pre_month_days[k]['month']
                        else:
                            db['belong_time'] = pre_month_days[k + 1]['month']
                        order_back_moneys.insert(b + 1, db)
                        month_money = 0.0
                        break
                else:
                    order_back_moneys[b][
                        'belong_time'] = pre_month_days[k]['month']
                    month_money = 0.0
                    total_back_money -= back_money
    order_back_moneys = [k for k in order_back_moneys if k[
        'back_time'] >= start_Q_month and k['back_time'] < end_Q_month]
    return order_back_moneys


# 格式化合同
def _order_to_dict(order, start_Q_month, end_Q_month, back_moneys, now_Q_back_moneys, all_outsource):
    dict_order = {}
    dict_order['client_name'] = order.client.name
    dict_order['order_path'] = order.info_path()
    dict_order['money'] = order.money
    dict_order['contract_status'] = order.contract_status
    dict_order['__tablename__'] = order.__tablename__
    if order.__tablename__ == 'bra_client_order':
        dict_order['media_info'] = '<br>'.join(['%s:%s' % (o.medium_group.name, o.media.name)
                                                for o in order.medium_orders])
    else:
        dict_order['media_info'] = u'豆瓣'
    dict_order['agent_name'] = order.agent.name
    dict_order['contract'] = order.contract.strip()
    dict_order['campaign'] = order.campaign
    dict_order['locations'] = order.locations
    dict_order['locations_cn'] = order.locations_cn
    dict_order['industry_cn'] = order.client.industry_cn
    dict_order['contract_status'] = order.contract_status
    dict_order['status'] = order.status
    order_back_money_data = _order_back_money_data(
        order, start_Q_month, end_Q_month, back_moneys)
    # 获取规定时间最后一次回款时间及回款总金额
    money_time = [k['back_time'].strftime(
        '%Y-%m-%d') for k in order_back_money_data if k['type'] == 'money' and k['order'] == order]
    money_time.reverse()
    if money_time:
        dict_order['money_time'] = money_time[-1]
    else:
        dict_order['money_time'] = None
    dict_order['money_sum'] = sum([k['money'] for k in order_back_money_data if k[
                                  'type'] == 'money' and k['order'] == order])
    # 获取规定时间最后一次返点发票时间及返点发票总金额
    invoice_time = [k['back_time'].strftime(
        '%Y-%m-%d') for k in order_back_money_data if k['type'] == 'invoice' and k['order'] == order]
    invoice_time.reverse()
    if invoice_time:
        dict_order['invoice_time'] = invoice_time[-1]
    else:
        dict_order['invoice_time'] = None
    dict_order['invoice_sum'] = sum([k['money'] for k in order_back_money_data if k[
                                    'type'] == 'invoice' and k['order'] == order])
    if order.__tablename__ == 'bra_douban_order':
        dict_order['b_type'] = 0
        dict_order['outsource_money'] = sum([o['money'] for o in all_outsource if o[
                                            'order_id'] == order.id and o['type'] == 'douban'])
        dict_order['profit'] = 0
    else:
        dict_order['outsource_money'] = sum([o['money'] for o in all_outsource if o[
                                            'order_id'] == order.id and o['type'] == 'client'])
        # 获取代理返点
        agent_rebate_value = order.client_order_agent_rebate_ai
        # 媒体返点
        media_rebate_value = 0
        # 媒体金额总和
        medium_money_total = 0
        b_type = []
        for m in order.medium_orders:
            b_type.append(m.media.b_type or 0)
            media_rebate_value += m.client_order_agent_rebate_ai
            medium_money_total += m.medium_money2
        # 分析订单业务类型：1，自营；2，增量；3，混搭（按增量计算）
        ex_date = datetime.datetime.strptime('2016-07-01', '%Y-%m-%d').date()
        if order.client_start < ex_date:
            dict_order['b_type'] = 0
            dict_order['profit'] = 0
        else:
            b_type = list(set(b_type))
            if len(b_type) > 1:
                dict_order['b_type'] = 1
            elif b_type == [1]:
                dict_order['b_type'] = 1
            else:
                dict_order['b_type'] = 0
            if order.money:
                dict_order['profit'] = (order.money - medium_money_total - agent_rebate_value -
                                        dict_order['outsource_money'] + media_rebate_value) / order.money
            else:
                dict_order['profit'] = 0
    # 保留两位小数
    dict_order['profit'] = float('%.2f' % (dict_order['profit']))
    dict_order['direct_sales'] = []
    dict_order['agent_sales'] = []
    dict_order['client_start'] = order.client_start
    dict_order['client_end'] = order.client_end
    # 媒介提成
    if dict_order['b_type']:
        dict_order['media_money'] = sum([k['money'] for k in order_back_money_data]) * dict_order['profit'] * 0.05
    else:
        dict_order['media_money'] = 0
    # 按销售类型计算提成
    for saler in order.direct_sales:
        d_saler = {}
        # 该销售是否发放提成，根绝完成率计算
        d_saler['str_formula_status'] = True
        d_saler['id'] = saler.id
        d_saler['name'] = saler.name
        d_saler['type'] = u'直客'
        d_saler['location_cn'] = saler.location_cn
        # 转正时间
        positive_date_cn = saler.positive_date_cn
        # 离职时间
        quit_date_cn = saler.quit_date_cn
        if quit_date_cn:
            quit_date = datetime.datetime.strptime(
                quit_date_cn, '%Y-%m-%d') + datetime.timedelta(days=90)
        else:
            quit_date = None
        # 离职后超过90天没提成，试用期没有提成
        if not positive_date_cn:
            d_saler['color'] = 'FFBB00'
        elif quit_date and quit_date < end_Q_month:
            d_saler['color'] = 'FF0000'
        # 判断销售是否有平分金额
        if len(set(order.locations)) > 1:
            l_count = len(set(order.locations))
        else:
            l_count = 1
        count = len(order.direct_sales)
        if saler.team.location == 3 and len(order.locations) > 1:
            count = len(order.direct_sales)
        elif saler.team.location == 3 and len(order.locations) == 1:
            count = len(order.agent_sales + order.direct_sales)

        d_saler['str_formula'] = ""
        commission_money = 0
        for b_money_obj in order_back_money_data:
            b_money = b_money_obj['money'] / count / l_count
            back_time = b_money_obj['back_time']
            if b_money:
                if int(dict_order['client_start'].year) < 2016:
                    belong_time = dict_order['client_start']
                else:
                    belong_time = b_money_obj['belong_time']
                commission = saler.commission(belong_time.year)
                if int(dict_order['client_start'].strftime('%Y')) <= 2015:
                    day_rate = 1
                    back_days = 0
                else:
                    back_days = (back_time.date() - dict_order['client_end']).days + 1
                    day_rate = _back_day_rate(back_days)
                if dict_order['b_type'] == 1:
                    completion = saler.completion_increment(belong_time)
                    if dict_order['profit'] < 0.15:
                        c_money = b_money * dict_order['profit'] * commission * 5
                        d_saler['str_formula'] += u"%s(回款金额) * %s(利润率) * %s(提成比例) * 5 = %s(%s月 提成信息)<br/>" % (
                            '%.2f' % (b_money), str(dict_order['profit']), str(commission), str(c_money),
                            belong_time.strftime('%Y-%m'))
                    else:
                        c_money = completion * commission * b_money * day_rate
                        # 计算公式
                        d_saler['str_formula'] += u"%s(增量完成率) * %s(提成比例) * %s(回款金额)\
                                                    * %s(账期系数,%s天) = %s(%s月 提成信息)<br/>" % (
                            str(completion), str(commission), '%.2f' % (b_money),
                            str(day_rate), str(back_days), '%.2f' % (c_money), belong_time.strftime('%Y-%m'))
                else:
                    ex_date = datetime.datetime.strptime('2016-07-01', '%Y-%m-%d').date()
                    if dict_order['profit'] < 0.05 and order.client_start > ex_date:
                        d_saler['str_formula_status'] = False
                    completion = saler.completion(belong_time)
                    c_money = completion * commission * b_money * day_rate
                    # 计算公式
                    d_saler['str_formula'] += u"%s(自营完成率) * %s(提成比例) * %s(回款金额) * %s(账期系数,%s天) = %s(%s月 提成信息)<br/>" % (
                        str(completion), str(commission), '%.2f' % (b_money),
                        str(day_rate), str(back_days), '%.2f' % (c_money), belong_time.strftime('%Y-%m'))
                commission_money += c_money
        d_saler['commission_money'] = commission_money
        dict_order['direct_sales'].append(d_saler)
        # dict_order['total_commission_money'] += commission_money
    for saler in order.agent_sales:
        d_saler = {}
        d_saler['str_formula_status'] = True
        d_saler['id'] = saler.id
        d_saler['name'] = saler.name
        d_saler['type'] = u'渠道'
        d_saler['location_cn'] = saler.location_cn
        positive_date_cn = saler.positive_date_cn
        quit_date_cn = saler.quit_date_cn
        if quit_date_cn:
            quit_date = datetime.datetime.strptime(
                quit_date_cn, '%Y-%m-%d') + datetime.timedelta(days=90)
        else:
            quit_date = None
        # 离职后超过90天没提成，试用期没有提成
        if not positive_date_cn:
            d_saler['color'] = 'FFBB00'
        elif quit_date and quit_date < end_Q_month:
            d_saler['color'] = 'FF0000'
        # 判断销售是否有平分金额
        if len(set(order.locations)) > 1:
            l_count = len(set(order.locations))
        else:
            l_count = 1
        count = len(order.agent_sales)
        if saler.team.location == 3 and len(order.locations) > 1:
            count = len(order.agent_sales)
        elif saler.team.location == 3 and len(order.locations) == 1:
            count = len(order.agent_sales + order.direct_sales)

        d_saler['str_formula'] = ""
        commission_money = 0
        for b_money_obj in order_back_money_data:
            b_money = b_money_obj['money'] / count / l_count
            back_time = b_money_obj['back_time']
            if b_money:
                if int(dict_order['client_start'].year) < 2016:
                    belong_time = dict_order['client_start']
                else:
                    belong_time = b_money_obj['belong_time']
                commission = saler.commission(belong_time.year)
                if int(dict_order['client_start'].strftime('%Y')) <= 2015:
                    day_rate = 1
                    back_days = 0
                else:
                    back_days = (back_time.date() - dict_order['client_end']).days + 1
                    day_rate = _back_day_rate(back_days)
                if dict_order['b_type'] == 1:
                    completion = saler.completion_increment(belong_time)
                    if dict_order['profit'] < 0.15:
                        c_money = b_money * dict_order['profit'] * commission * 5
                        d_saler['str_formula'] += u"%s(回款金额) * %s(利润率) * %s(提成比例) * 5 = %s(%s月 提成信息)<br/>" % (
                            '%.2f' % (b_money), str(dict_order['profit']), str(commission), str(c_money),
                            belong_time.strftime('%Y-%m'))
                    else:
                        c_money = completion * commission * b_money * day_rate
                        # 计算公式
                        d_saler['str_formula'] += u"%s(增量完成率) * %s(提成比例) * %s(回款金额)\
                                                    * %s(账期系数,%s天) = %s(%s月 提成信息)<br/>" % (
                            str(completion), str(commission), '%.2f' % (b_money),
                            str(day_rate), str(back_days), '%.2f' % (c_money), belong_time.strftime('%Y-%m'))
                else:
                    ex_date = datetime.datetime.strptime('2016-07-01', '%Y-%m-%d').date()
                    if dict_order['profit'] < 0.05 and order.client_start > ex_date:
                        d_saler['str_formula_status'] = False
                    completion = saler.completion(belong_time)
                    c_money = completion * commission * b_money * day_rate
                    # 计算公式
                    d_saler['str_formula'] += u"%s(自营完成率) * %s(提成比例) * %s(回款金额) * %s(账期系数,%s天) = %s(%s月 提成信息)<br/>" % (
                        str(completion), str(commission), '%.2f' % (b_money),
                        str(day_rate), str(back_days), '%.2f' % (c_money), belong_time.strftime('%Y-%m'))
                commission_money += c_money
        d_saler['commission_money'] = commission_money
        dict_order['agent_sales'].append(d_saler)
    dict_order['salers_count'] = len(dict_order['direct_sales'] + dict_order['agent_sales'])
    dict_order['total_commission_money'] = sum([u['commission_money']
                                                for u in dict_order['direct_sales'] + dict_order['agent_sales']])
    return dict_order


# 格式化回款
def _dict_back_money(back_money, type='money'):
    dict_back_money = {}
    dict_back_money['type'] = type
    dict_back_money['money'] = back_money.money
    dict_back_money['back_time'] = back_money.back_time
    order = back_money.order
    dict_back_money['order'] = order
    dict_back_money['order_id'] = back_money.order.id
    return dict_back_money


# 销售提成
@account_commission_bp.route('/saler', methods=['GET'])
def saler():
    if not (g.user.is_super_leader() or g.user.is_finance()):
        abort(403)
    now_year = request.values.get('year', '')
    now_Q = request.values.get('Q', '')
    location_id = int(request.values.get('location_id', 0))
    if not now_year and not now_Q:
        now_date = datetime.date.today()
        now_year = now_date.strftime('%Y')
        now_month = now_date.strftime('%m')
        now_Q = check_month_get_Q(now_month)
    Q_monthes = check_Q_get_monthes(now_Q)
    start_Q_month = datetime.datetime(int(now_year), int(Q_monthes[0]), 1)
    # 获取下季度的第一天为本季度的结束时间
    d = cal.monthrange(int(now_year), int(Q_monthes[-1]))
    end_Q_month = datetime.datetime(
        int(now_year), int(Q_monthes[-1]), d[1]) + datetime.timedelta(days=1)
    # 获取该季度及之前所有回款及返点发票
    client_back_moneys = [_dict_back_money(
        k, 'money') for k in BackMoney.query.filter(BackMoney.back_time < end_Q_month)]
    client_back_moneys += [_dict_back_money(k, 'invoice') for k in BackInvoiceRebate.query.filter(
        BackInvoiceRebate.back_time < end_Q_month)]
    douban_back_moneys = [_dict_back_money(k, 'money') for k in DoubanBackMoney.query.filter(
        DoubanBackMoney.back_time < end_Q_month)]
    douban_back_moneys += [_dict_back_money(k, 'invoice') for k in DoubanBackInvoiceRebate.query.filter(
        DoubanBackInvoiceRebate.back_time < end_Q_month)]
    # 获取当前季度所有回款
    now_Q_client_back_moneys = [
        k for k in client_back_moneys if k['back_time'] >= start_Q_month]
    now_Q_douban_back_moneys = [
        k for k in douban_back_moneys if k['back_time'] >= start_Q_month]

    # 获取当季度回款的所有合同
    client_orders = list(set([k['order'] for k in now_Q_client_back_moneys]))
    douban_orders = list(set([k['order'] for k in now_Q_douban_back_moneys]))
    # 获取所有外包数据
    all_outsource = _all_outsource()
    orders = [_order_to_dict(k, start_Q_month, end_Q_month, client_back_moneys,
                             now_Q_client_back_moneys, all_outsource) for k in client_orders
              if k.contract_status not in [7, 8, 9] and k.status == 1 and k.contract]
    orders += [_order_to_dict(k, start_Q_month, end_Q_month, douban_back_moneys,
                              now_Q_douban_back_moneys, all_outsource) for k in douban_orders
               if k.contract_status not in [7, 8, 9] and k.status == 1 and k.contract]
    if location_id:
        orders = [k for k in orders if location_id in k['locations']]
    orders = sorted(orders, key=operator.itemgetter('client_start'), reverse=False)
    if request.values.get('action') == 'download':
        return write_report_excel(Q=now_Q, now_year=now_year, orders=orders)
    return tpl('/account/commission/saler.html', Q=now_Q, now_year=now_year,
               Q_monthes=Q_monthes, location_id=location_id, orders=orders)
