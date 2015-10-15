# -*- coding: utf-8 -*-
import datetime

from flask import Blueprint, g, abort, redirect, flash, url_for, request
from flask import render_template as tpl

from models.user import User
from models.account.saler import (Performance, PerformanceUser, TEAM_LOCATION_HUABEI,
                                  TEAM_LOCATION_HUADONG, TEAM_LOCATION_HUANAN)

account_performance_bp = Blueprint(
    'account_performance', __name__, template_folder='../../templates/account/performance/')


@account_performance_bp.route('/', methods=['GET'])
def index():
    if not (g.user.is_leader() or g.user.is_super_leader()):
        return abort(404)
    huabei_performances = []
    huanan_performances = []
    huadong_performances = []
    if g.user.is_leader():
        if g.user.team.location == TEAM_LOCATION_HUABEI:
            huabei_performances = Performance.query.filter_by(
                location=TEAM_LOCATION_HUABEI)
        elif g.user.team.location == TEAM_LOCATION_HUADONG:
            huadong_performances = Performance.query.filter_by(
                location=TEAM_LOCATION_HUADONG)
        elif g.user.team.location == TEAM_LOCATION_HUANAN:
            huanan_performances = Performance.query.filter_by(
                location=TEAM_LOCATION_HUANAN)
    if g.user.is_super_leader():
        huabei_performances = Performance.query.filter_by(
            location=TEAM_LOCATION_HUABEI)
        huadong_performances = Performance.query.filter_by(
            location=TEAM_LOCATION_HUADONG)
        huanan_performances = Performance.query.filter_by(
            location=TEAM_LOCATION_HUANAN)
    return tpl('/account/performance/index.html', huabei_performances=huabei_performances,
               huadong_performances=huadong_performances, huanan_performances=huanan_performances)


@account_performance_bp.route('/create', methods=['GET', 'POST'])
def create():
    if g.user.is_searchad_member() and (not g.user.is_admin()) and (not g.user.is_super_leader()):
        users = [u for u in User.all() if u.is_search_saler and u.is_active()]
    else:
        users = [u for u in User.all() if u.is_out_saler and u.is_active()]
    huabei_users = [u for u in users if u.location == TEAM_LOCATION_HUABEI]
    huadong_users = [u for u in users if u.location == TEAM_LOCATION_HUADONG]
    huanan_users = [u for u in users if u.location == TEAM_LOCATION_HUANAN]
    if request.method == 'POST':
        location = int(request.values.get('location', 1))
        year = int(request.values.get('year', datetime.datetime.now().year))
        q_month = request.values.get('q_month', 'Q1')
        t_money = float(request.values.get('t_money', 0))
        user_moneys = {}
        if location == TEAM_LOCATION_HUABEI:
            for k in huabei_users:
                u_money = float(request.values.get('money_' + str(k.id), 0))
                user_moneys[str(k.id)] = u_money
        elif location == TEAM_LOCATION_HUADONG:
            for k in huadong_users:
                u_money = float(request.values.get('money_' + str(k.id), 0))
                user_moneys[str(k.id)] = u_money
        elif location == TEAM_LOCATION_HUANAN:
            for k in huanan_users:
                u_money = float(request.values.get('money_' + str(k.id), 0))
                user_moneys[str(k.id)] = u_money
        try:
            performance = Performance.add(location=location,
                                          year=year,
                                          q_month=q_month,
                                          t_money=t_money,
                                          status=1,
                                          create_time=datetime.date.today(),
                                          creator=g.user,
                                          )
            if performance:
                for k, v in user_moneys.iteritems():
                    PerformanceUser.add(
                        user=User.get(int(k)),
                        money=float(v),
                        performance=performance,
                        year=year,
                        q_month=q_month,
                        create_time=datetime.date.today()
                    )
                flash(u'%s%s销售计划添加成功' % (str(year), q_month), 'success')
                return redirect(url_for('account_performance.index'))
            else:
                flash(u'已存在改季度销售计划', 'danger')
                return redirect(url_for('account_performance.create'))
        except:
            flash(u'已存在改季度销售计划', 'danger')
    return tpl('/account/performance/create.html', huabei_users=huabei_users,
               huadong_users=huadong_users, huanan_users=huanan_users)


@account_performance_bp.route('/<pid>/update', methods=['GET', 'POST'])
def update(pid):
    performance = Performance.get(pid)
    if g.user.is_searchad_member() and (not g.user.is_admin()) and (not g.user.is_super_leader()):
        users = [u for u in User.all() if u.is_search_saler and u.is_active()]
    else:
        users = [u for u in User.all() if u.is_out_saler and u.is_active()]
    huabei_users = [u for u in users if u.location == TEAM_LOCATION_HUABEI]
    huadong_users = [u for u in users if u.location == TEAM_LOCATION_HUADONG]
    huanan_users = [u for u in users if u.location == TEAM_LOCATION_HUANAN]
    if request.method == 'POST':
        year = int(request.values.get('year', datetime.datetime.now().year))
        q_month = request.values.get('q_month', 'Q1')
        t_money = float(request.values.get('t_money', 0))

        user_moneys = {}
        if performance.location == TEAM_LOCATION_HUABEI:
            for k in huabei_users:
                u_money = float(request.values.get('money_' + str(k.id), 0))
                user_moneys[str(k.id)] = u_money
        elif performance.location == TEAM_LOCATION_HUADONG:
            for k in huadong_users:
                u_money = float(request.values.get('money_' + str(k.id), 0))
                user_moneys[str(k.id)] = u_money
        elif performance.location == TEAM_LOCATION_HUANAN:
            for k in huanan_users:
                u_money = float(request.values.get('money_' + str(k.id), 0))
                user_moneys[str(k.id)] = u_money

        try:
            performance.year = year
            performance.q_month = q_month
            performance.t_money = t_money
            performance.create_time = datetime.date.today()
            performance.creator = g.user
            performance.save()

            performance.performance_user_money.delete()
            for k, v in user_moneys.iteritems():
                PerformanceUser.add(
                    user=User.get(int(k)),
                    money=float(v),
                    performance=performance,
                    year=year,
                    q_month=q_month,
                    create_time=datetime.date.today()
                )

            flash(u'%s%s销售计划修改成功' % (str(year), q_month), 'success')
            return redirect(url_for('account_performance.update', pid=pid))
        except:
            flash(u'已存在改季度销售计划', 'danger')
            return redirect(url_for('account_performance.update', pid=pid))
    return tpl('/account/performance/update.html', huabei_users=huabei_users,
               huadong_users=huadong_users, huanan_users=huanan_users,
               performance=performance)
