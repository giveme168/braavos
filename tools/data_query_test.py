# encoding: utf-8
import os
import datetime
import sys
# sys.path.append('/Users/guoyu1/workspace/inad/braavos')
sys.path.append('/home/inad/apps/braavos/releases/current')

from app import app

from models.order import MediumOrderExecutiveReport
from models.douban_order import DoubanOrderExecutiveReport
from models.client import Client
from models.medium import Medium

if __name__ == '__main__':
    start_date_month = datetime.datetime.strptime('2015-01-01', '%Y-%m-%d')
    end_date_month = datetime.datetime.strptime('2015-12-01', '%Y-%m-%d')
    medium_orders = MediumOrderExecutiveReport.query.filter(
        MediumOrderExecutiveReport.month_day >= start_date_month,
        MediumOrderExecutiveReport.month_day <= end_date_month)
    douban_orders = DoubanOrderExecutiveReport.query.filter(
        DoubanOrderExecutiveReport.month_day >= start_date_month,
        DoubanOrderExecutiveReport.month_day <= end_date_month)
    medium_orders = [{'month_day': k.month_day, 'client_id': k.client_order.client.id,
                      'status': k.status, 'medium_id': int(k.order.medium_id),
                      'medium_name':k.order.medium.name,
                      'sale_money': k.sale_money, 'client_name': k.client_order.client.name,
                      'medium_money2': k.medium_money2,
                      } for k in medium_orders if k.status == 1 and k.client_order.status==1]
    douban_orders = [{'month_day': k.month_day, 'client_id': k.douban_order.client.id,
                      'status': k.status, 'money': k.money,
                      'client_name': k.douban_order.client.name,
                      } for k in douban_orders if k.status == 1 and k.douban_order.status ==1]
    '''
    youli_data = [{'client_id': k['client_id'],
                   'client_name':k['client_name'],
                   'money':k['medium_money2']}
                  for k in medium_orders if k['medium_id'] == 3]
    wuxian_data = [{'client_id': k['client_id'],
                    'client_name':k['client_name'],
                    'money':k['medium_money2']}
                   for k in medium_orders if k['medium_id'] == 8]
    '''

    medium_date = [{'client_id': k['client_id'],
                    'client_name':k['client_name'],
                    'money':k['medium_money2'],
                    'medium_id':k['medium_id'],
                    'medium_name':k['medium_name']}
                   for k in medium_orders]

    douban_date = [{'client_id': k['client_id'],
                    'client_name':k['client_name'],
                    'money':k['money']}
                   for k in douban_orders]
    '''
    client_data = {}
    for k in Client.all():
        client_data[k.name] = 0
    for k in douban_date+medium_date:
        if client_data.has_key(k['client_name']):
            client_data[k['client_name']] += k['money']
    client_data = sorted(client_data.iteritems(), key = lambda x:x[1])
    client_data.reverse()
    for k in client_data:
        if k[1]:
            print k[0]
    '''
    medium_data = {}
    for k in Medium.all():
        if k.id in [52, 51, 46, 14,9,7,6,5,4]:
            medium_data[k.name] = 0
    for k in medium_date:
        if medium_data.has_key(k['medium_name']):
            medium_data[k['medium_name']] += k['money']
    medium_data = sorted(medium_data.iteritems(), key = lambda x:x[1])
    medium_data.reverse()
    for k in medium_data:
        if k[1]:
            print k[1]