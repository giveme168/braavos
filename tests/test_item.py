from models.item import AdItem, AdSchedule
from helper import add_item, add_schedule


def test_item(session):
    item = add_item()

    item2 = AdItem.get(item.id)
    assert item2 is not None


def test_schedule(session):
    schedule = add_schedule()

    schedule2 = AdSchedule.get(schedule.id)
    assert schedule2 is not None
