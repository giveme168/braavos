# encoding: utf-8
import sys
import datetime
sys.path.append('/Users/guoyu1/workspace/inad/braavos')
# sys.path.append('/home/inad/apps/braavos/releases/current')

from app import app
from models.outsource import OutSource, DoubanOutSource
from models.client_order import OtherCost
from models.douban_order import OtherCost as DoubanOtherCost


# 导入尚典外包
if __name__ == '__main__':
    outsources = OutSource.all()
    outsources = [o for o in outsources if o.target_id == 271]
    for o in outsources:
        company = o.target.name
        client_order = o.medium_order.client_order
        money = o.num
        if o.type == 9:
            type = 3
        elif o.type == 8:
            type = 2
        elif o.type == 2:
            type = 1
        else:
            type = 2
        invoice = ''
        on_time = o.medium_order.medium_start
        create_time = datetime.datetime.now()
        OtherCost.add(
            company=company,
            client_order=client_order,
            money=money,
            type=type,
            invoice=invoice,
            on_time=on_time,
            create_time=create_time
        )

    outsources = DoubanOutSource.all()
    outsources = [o for o in outsources if o.target_id == 271]
    for o in outsources:
        company = o.target.name
        douban_order = o.douban_order
        money = o.num
        if o.type == 9:
            type = 3
        elif o.type == 8:
            type = 2
        elif o.type == 2:
            type = 1
        else:
            type = 2
        invoice = ''
        on_time = o.douban_order.client_start
        create_time = datetime.datetime.now()
        DoubanOtherCost.add(
            company=company,
            douban_order=douban_order,
            money=money,
            type=type,
            invoice=invoice,
            on_time=on_time,
            create_time=create_time
        )
