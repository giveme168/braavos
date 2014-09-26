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


def get_export_schedules_units(_date=datetime.date.today()):
    schedules = AdSchedule.export_schedules(_date)
    return [schedule_info(s) for s in schedules], units_info(schedules)


def schedule_info(schedule):
    item = schedule.item
    ret = {'schedule_id': schedule.id,
           'item_id': item.id,
           'units': [u.id for u in schedule.units],
           'materials': [material_info(m) for m in item.materials],
           'schedule_num': schedule.num,
           'start_time': schedule.start.strftime(TIME_FORMAT),
           'end_time': schedule.end.strftime(TIME_FORMAT),
           }
    return ret


def units_info(schedules):
    ret = {}
    for s in schedules:
        for u in s.units:
            u_info = ret.get(u.id, {'items': [], 'info': unit_info(u)})
            items_set = set(u_info.get('items', []))
            items_set.add(s.item.id)
            u_info['items'] = list(items_set)
            ret[u.id] = u_info
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
    ad_schedules_key = "AD:Date:%s:Schedules" % _date.strftime(DATE_FORMAT)
    ad_units_key = "AD:Date:%s:Units" % _date.strftime(DATE_FORMAT)
    s_info, u_info = get_export_schedules_units()
    print s_info
    print u_info
    redis_client.setex(ad_schedules_key, DATA_EXPIRES_TIME, json.dumps(s_info))
    redis_client.setex(ad_units_key, DATA_EXPIRES_TIME, json.dumps(u_info))
