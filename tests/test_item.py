import datetime

from models.item import AdItem, AdSchedule
from helper import add_item, add_schedule


def test_item(session):
    item = add_item()

    item2 = AdItem.get(item.id)
    assert item2 is not None


def test_item_delivery(session):
    item = add_item()
    date = datetime.date.today()
    assert item.get_monitor_num(date) == 0
    item.set_monitor_num(date, 500)
    assert item.get_monitor_num(date) == 500


def test_schedule(session):
    schedule = add_schedule()

    schedule2 = AdSchedule.get(schedule.id)
    assert schedule2 is not None
