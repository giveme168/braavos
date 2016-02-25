# encoding: utf-8
import sys
sys.path.append('/Users/guoyu1/workspace/inad/braavos')
# sys.path.append('/home/inad/apps/braavos/releases/current')

from app import app

from models.client_order import ClientOrder, ClientOrderExecutiveReport
from models.order import MediumOrderExecutiveReport
from models.framework_order import FrameworkOrder
from models.medium_framework_order import MediumFrameworkOrder
from models.douban_order import DoubanOrder, DoubanOrderExecutiveReport

from searchAd.models.order import searchAdMediumOrderExecutiveReport
from searchAd.models.rebate_order import searchAdRebateOrder, searchAdRebateOrderExecutiveReport
from searchAd.models.client_order import searchAdClientOrder, searchAdClientOrderExecutiveReport
from searchAd.models.framework_order import searchAdFrameworkOrder


def _insert_search_executive_report(order, rtype):
    if order.contract_status not in [2, 4, 5, 20]:
        return False
    if order.__tablename__ == 'searchad_bra_rebate_order':
        if rtype:
            searchAdRebateOrderExecutiveReport.query.filter_by(
                rebate_order=order).delete()
        for k in order.pre_month_money():
            if not searchAdRebateOrderExecutiveReport.query.filter_by(rebate_order=order, month_day=k['month']).first():
                er = searchAdRebateOrderExecutiveReport.add(rebate_order=order,
                                                            money=k['money'],
                                                            month_day=k[
                                                                'month'],
                                                            days=k['days'],
                                                            create_time=None)
                er.save()
    elif order.__tablename__ == 'searchAd_bra_client_order':
        if rtype:
            searchAdClientOrderExecutiveReport.query.filter_by(
                client_order=order).delete()
            searchAdMediumOrderExecutiveReport.query.filter_by(
                client_order=order).delete()
        for k in order.pre_month_money():
            if not searchAdClientOrderExecutiveReport.query.filter_by(client_order=order, month_day=k['month']).first():
                er = searchAdClientOrderExecutiveReport.add(client_order=order,
                                                            money=k['money'],
                                                            month_day=k[
                                                                'month'],
                                                            days=k['days'],
                                                            create_time=None)
                er.save()
        for k in order.medium_orders:
            for i in k.pre_month_medium_orders_money():
                if not searchAdMediumOrderExecutiveReport.query.filter_by(client_order=order,
                                                                          order=k, month_day=i['month']).first():
                    er = searchAdMediumOrderExecutiveReport.add(client_order=order,
                                                                order=k,
                                                                medium_money=0,
                                                                medium_money2=i[
                                                                    'medium_money2'],
                                                                sale_money=i[
                                                                    'sale_money'],
                                                                month_day=i[
                                                                    'month'],
                                                                days=i['days'],
                                                                create_time=None)
                    er.save()
    elif order.__tablename__ == 'searchAd_bra_order':
        if rtype:
            searchAdMediumOrderExecutiveReport.query.filter_by(
                order=order).delete()
        for i in order.pre_month_medium_orders_money():
            if not searchAdMediumOrderExecutiveReport.query.filter_by(client_order=order.client_order,
                                                                      order=order, month_day=i['month']).first():
                er = searchAdMediumOrderExecutiveReport.add(client_order=order.client_order,
                                                            order=order,
                                                            medium_money=0,
                                                            medium_money2=i[
                                                                'medium_money2'],
                                                            sale_money=i[
                                                                'sale_money'],
                                                            month_day=i[
                                                                'month'],
                                                            days=i['days'],
                                                            create_time=None)
                er.save()
    return True


def _insert_zhiqu_executive_report(order, rtype):
    if order.contract == '' or order.contract_status not in [2, 4, 5, 20]:
        return False
    if order.__tablename__ == 'bra_douban_order':
        if rtype:
            DoubanOrderExecutiveReport.query.filter_by(
                douban_order=order).delete()
        for k in order.pre_month_money():
            if not DoubanOrderExecutiveReport.query.filter_by(douban_order=order, month_day=k['month']).first():
                er = DoubanOrderExecutiveReport.add(douban_order=order,
                                                    money=k['money'],
                                                    month_day=k['month'],
                                                    days=k['days'],
                                                    create_time=None)
                er.save()
    elif order.__tablename__ == 'bra_client_order':
        if rtype:
            ClientOrderExecutiveReport.query.filter_by(
                client_order=order).delete()
            MediumOrderExecutiveReport.query.filter_by(
                client_order=order).delete()
        for k in order.pre_month_money():
            if not ClientOrderExecutiveReport.query.filter_by(client_order=order, month_day=k['month']).first():
                er = ClientOrderExecutiveReport.add(client_order=order,
                                                    money=k['money'],
                                                    month_day=k['month'],
                                                    days=k['days'],
                                                    create_time=None)
                er.save()
        for k in order.medium_orders:
            for i in k.pre_month_medium_orders_money():
                if not MediumOrderExecutiveReport.query.filter_by(client_order=order,
                                                                  order=k, month_day=i['month']).first():
                    er = MediumOrderExecutiveReport.add(client_order=order,
                                                        order=k,
                                                        medium_money=i[
                                                            'medium_money'],
                                                        medium_money2=i[
                                                            'medium_money2'],
                                                        sale_money=i[
                                                            'sale_money'],
                                                        month_day=i['month'],
                                                        days=i['days'],
                                                        create_time=None)
                    er.save()
    elif order.__tablename__ == 'bra_order':
        if rtype:
            MediumOrderExecutiveReport.query.filter_by(order=order).delete()
        for i in order.pre_month_medium_orders_money():
            if not MediumOrderExecutiveReport.query.filter_by(client_order=order.client_order,
                                                              order=order, month_day=i['month']).first():
                er = MediumOrderExecutiveReport.add(client_order=order.client_order,
                                                    order=order,
                                                    medium_money=i[
                                                        'medium_money'],
                                                    medium_money2=i[
                                                        'medium_money2'],
                                                    sale_money=i[
                                                        'sale_money'],
                                                    month_day=i['month'],
                                                    days=i['days'],
                                                    create_time=None)
                er.save()
    return True

if __name__ == '__main__':
    client_orders = ClientOrder.all()
    douban_orders = DoubanOrder.all()
    framework_orders = FrameworkOrder.all()
    medium_framework_orders = MediumFrameworkOrder.all()
    search_client_orders = searchAdClientOrder.all()
    search_rebate_orders = searchAdRebateOrder.all()
    search_framework_orders = searchAdFrameworkOrder.all()

    for c in client_orders:
        c.client_start_year = c.client_start.year
        c.client_end_year = c.client_end.year
        c.save()
        _insert_zhiqu_executive_report(c, 'reload')

    for d in douban_orders:
        d.client_start_year = d.client_start.year
        d.client_end_year = d.client_end.year
        d.save()
        _insert_zhiqu_executive_report(d, 'reload')

    for f in framework_orders:
        f.client_start_year = f.client_start.year
        f.client_end_year = f.client_end.year
        f.save()

    for mf in medium_framework_orders:
        mf.client_start_year = mf.client_start.year
        mf.client_end_year = mf.client_end.year
        mf.save()

    for sc in search_client_orders:
        sc.client_start_year = sc.client_start.year
        sc.client_end_year = sc.client_end.year
        sc.save()
        _insert_search_executive_report(sc, 'reload')

    for sr in search_rebate_orders:
        sr.client_start_year = sr.client_start.year
        sr.client_end_year = sr.client_end.year
        sr.save()
        _insert_search_executive_report(sr, 'reload')

    for sf in search_framework_orders:
        sf.client_start_year = sf.client_start.year
        sf.client_end_year = sf.client_end.year
        sf.save()
