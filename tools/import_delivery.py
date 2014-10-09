# -*- coding: UTF-8 -*-
import os
import sys
import datetime
sys.path.insert(0, os.path.abspath('.'))

from factory import create_app
from config import config_object

app = create_app(config_object)

from libs.redis_client import redis
from models.user import User, Team
from models.medium import Medium, AdSize, AdUnit, AdPosition
from models.client import Client, Agent
from models.order import Order
from models.item import AdSchedule, AdItem
from models.material import Material
from models.consts import DATE_FORMAT
from models.delivery import DELIVERY_TYPE_MONITOR, DELIVERY_TYPE_CLICK


def import_target_delivery(date, delivery_type, target, target_cls):
    unit_key_pattern = "AD:Date:%s:DeliveryType:%s:%s:*" % (date.strftime(DATE_FORMAT),
                                                            delivery_type,
                                                            target)
    for k in redis.keys(unit_key_pattern):
        uid = k.split(target + ':')[-1]
        num = redis.get(k)
        unit = target_cls.get(uid)
        unit.set_delivery_num(date, delivery_type, num)


def import_unit_delivery(date):
    target = "Unit"
    target_cls = AdUnit
    delivery_type = DELIVERY_TYPE_MONITOR
    import_target_delivery(date, delivery_type, target, target_cls)
    delivery_type = DELIVERY_TYPE_CLICK
    import_target_delivery(date, delivery_type, target, target_cls)


def import_material_delivery(date):
    target = "Material"
    target_cls = Material
    delivery_type = DELIVERY_TYPE_MONITOR
    import_target_delivery(date, delivery_type, target, target_cls)
    delivery_type = DELIVERY_TYPE_CLICK
    import_target_delivery(date, delivery_type, target, target_cls)


def import_item_delivery(date):
    target = "Item"
    target_cls = AdItem
    delivery_type = DELIVERY_TYPE_MONITOR
    import_target_delivery(date, delivery_type, target, target_cls)
    delivery_type = DELIVERY_TYPE_CLICK
    import_target_delivery(date, delivery_type, target, target_cls)


def import_delivery(date):
    import_unit_delivery(date)
    import_material_delivery(date)
    import_item_delivery(date)

if __name__ == '__main__':
    _date = datetime.date.today()
    import_delivery(_date)
