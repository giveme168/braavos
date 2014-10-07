# -*- coding: UTF-8 -*-
import os
import sys
import datetime
import json
from redis import StrictRedis
sys.path.insert(0, os.path.abspath('.'))

from factory import create_app
from config import config_object

app = create_app(config_object)
redis_client = StrictRedis(host='localhost', port=6379, db=0)

from models.user import User, Team
from models.medium import Medium, AdSize, AdUnit, AdPosition
from models.client import Client, Agent
from models.order import Order
from models.item import AdSchedule
from models.material import Material
from models.consts import TIME_FORMAT, DATE_FORMAT

DATA_EXPIRES_TIME = 60 * 60 * 24


def get_export_items(_date):
    """所有该日期需要投放的排期, 广告单元索引"""
    schedules = AdSchedule.export_schedules(_date)
    return items_info_by_schedule(schedules)


def items_info_by_schedule(schedules):
    """根据排期返回订单项信息的字典"""
    ret = {}
    for s in schedules:
        ret[s.item.id] = item_info(s, s.item)
    return ret


def item_info(schedule, item):
    """排期信息"""
    ret = {'schedule_id': schedule.id,  # 排期id
           'item_id': item.id,  # 订单项id
           'units': [u.id for u in schedule.units],  # 投放单元
           'materials': [material_info(m) for m in item.materials],  # 投放素材
           'schedule_num': schedule.num,  # 投放量
           'start_time': schedule.start.strftime(TIME_FORMAT),  # 起始时间
           'end_time': schedule.end.strftime(TIME_FORMAT),  # 结束时间
           }
    return ret


def get_export_units(_date):
    """广告单元索引信息,(订单项, 单元尺寸)"""
    ret = {}
    for u in AdUnit.all():
        ret[str(u.id)] = {'items': [str(i.id) for i in u.online_order_items_by_date(_date)], 'info': unit_info(u)}
    return ret


def unit_info(unit):
    ret = {'unit_id': unit.id,
           'width': unit.size.width,
           'height': unit.size.height,
           'margin': unit.margin,
           'target': unit.target_cn,
           'medium': unit.medium.id}
    return ret


def material_info(material):
    ret = {'material_id': material.id,
           'html': material.html}
    return ret


if __name__ == '__main__':
    _date = datetime.date.today()
    ad_items_key = "AD:Date:%s:Items" % _date.strftime(DATE_FORMAT)
    ad_units_key = "AD:Date:%s:Units" % _date.strftime(DATE_FORMAT)
    i_info = get_export_items(datetime.date.today())
    u_info = get_export_units(datetime.date.today())
    redis_client.setex(ad_items_key, DATA_EXPIRES_TIME, json.dumps(i_info))
    redis_client.setex(ad_units_key, DATA_EXPIRES_TIME, json.dumps(u_info))
