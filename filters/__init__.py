#-*- coding: UTF-8 -*-
from models.item import ITEM_STATUS_ACTION_CN


def item_status_action_cn(action):
    return ITEM_STATUS_ACTION_CN[action]


def register_filter(app):
    env = app.jinja_env
    env.filters['item_status_action_cn'] = item_status_action_cn
