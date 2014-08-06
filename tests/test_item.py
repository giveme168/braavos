from datetime import datetime, timedelta

from models.item import AdItem, AdSchedule
from test_order import _add_order
from test_medium import _add_position
from test_user import _add_user


def _add_item():
    order = _add_order()
    position = _add_position('testposition')
    user = _add_user('testuseritem', 'pwd')
    item = AdItem(order, 0, 0, position, user, datetime.now())
    item.add()
    return item


def _add_schedule():
    item = _add_item()
    start = datetime.today()
    end = start + timedelta(days=1, seconds=-1)
    schedule = AdSchedule(item, 300, start, end)
    schedule.add()
    return schedule


def test_item(session):
    item = _add_item()

    item2 = AdItem.get(item.id)
    assert item2 is not None


def test_schedule(session):
    schedule = _add_schedule()

    schedule2 = AdSchedule.get(schedule.id)
    assert schedule2 is not None
