import datetime

from models.medium import Medium, AdSize, AdUnit, AdPosition
from helper import add_medium, add_size, add_unit, add_position


def test_medium(session):
    medium = add_medium('testmedium')

    medium2 = Medium.get(medium.id)
    assert medium2.name == 'testmedium'


def test_size(session):
    size = add_size(300, 50)

    size2 = AdSize.get(size.id)
    assert size2.width == 300
    assert size2.height == 50

    size.width = 400
    size.height = 80
    size.save()

    size3 = AdSize.get(size.id)
    assert size3.width == 400
    assert size3.height == 80

    size4 = add_size(400, 80)
    assert size4.id != size3.id
    assert size4 == size3


def test_unit(session):
    unit = add_unit('testunit', 300)

    unit2 = AdUnit.get(unit.id)
    assert unit2.name == 'testunit'
    assert unit2.estimate_num == 300


def test_unit_delivery(session):
    unit = add_unit('testunit', 300)
    date = datetime.date.today()
    assert unit.get_monitor_num(date) == 0
    unit.set_monitor_num(date, 500)
    assert unit.get_monitor_num(date) == 500


def test_position(session):
    position = add_position('testposition')

    position2 = AdPosition.get(position.id)
    assert position2.name == 'testposition'

    unit = add_unit('testunit', 300)
    assert len(position.units) == 0
    position.units = [unit]

    position3 = AdPosition.get(position.id)
    assert unit in position3.units
    assert position3 in unit.positions
