from datetime import date

from models.item import AdSchedule, AdItem, ITEM_STATUS_ACTION_PRE_ORDER
from helper import add_unit, add_position, add_item
from models.user import User


def test_schedule(session):
    unit1 = add_unit('unit1', 800)
    unit2 = add_unit('unit2', 700)
    position1 = add_position('position1')
    position2 = add_position('position2')
    position1.units = [unit1, unit2]
    position2.units = [unit1, unit2]

    assert unit1.estimate_num == 800
    assert unit2.estimate_num == 700
    assert position1.estimate_num == unit1.estimate_num + unit2.estimate_num
    assert position2.estimate_num == unit1.estimate_num + unit2.estimate_num

    item1 = add_item(position=position1)
    item2 = add_item(position=position2)

    _date = date.today()

    assert position1.schedule_num(_date) == 0
    assert position2.schedule_num(_date) == 0

    assert unit1.schedule_num(_date) == 0
    assert unit2.schedule_num(_date) == 0

    assert unit1.retain_num(_date) == 800
    assert unit2.retain_num(_date) == 700

    assert position1.retain_num(_date) == 1500
    assert position2.retain_num(_date) == 1500

    AdSchedule.add(item1, 500, _date)
    AdSchedule.add(item2, 100, _date)

    user = User.get_by_email('testuser1@inad.com')
    AdItem.update_items_with_action([item1], ITEM_STATUS_ACTION_PRE_ORDER, user)
    AdItem.update_items_with_action([item2], ITEM_STATUS_ACTION_PRE_ORDER, user)

    assert position1.schedule_num(_date) == 500
    assert position2.schedule_num(_date) == 100

    assert unit1.schedule_num(_date) == 320
    assert unit2.schedule_num(_date) == 280

    assert unit1.retain_num(_date) == 480
    assert unit2.retain_num(_date) == 420

    assert position1.retain_num(_date) == 900
    assert position2.retain_num(_date) == 900
