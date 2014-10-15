# -*- coding: utf-8 -*-
from datetime import date
from pytest_bdd import scenario, given, when, then

from models.item import AdSchedule, AdItem, ITEM_STATUS_ACTION_PRE_ORDER
from models.user import User
from helper import add_unit, add_position, add_item, get_position
from .test_consts import TEST_POSITION, TEST_UNIT


@scenario('schedule_behaviors.feature', 'add one unit to a position')
def test_schedule_behaviros():
    pass


@given('I have a position with one unit. And the estimate_num of the unit is 800')
def init_one_postion(session):
    unit = add_unit(TEST_UNIT, 800)
    position = add_position('test_position')
    position.units = [unit]


@when('order an item with 600 and change its state to per_order')
def order_item(session):
    item = add_item(get_position(TEST_POSITION))
    AdSchedule(item, 600, date.today())
    user = User.get_by_email('testuser1@inad.com')
    AdItem.update_items_with_action([item], ITEM_STATUS_ACTION_PRE_ORDER, user)


@then('order successfully')
def then_add(session):
    position = get_position(TEST_POSITION)
    assert position.estimate_num == 800
    assert position.retain_num(date.today()) == 200
