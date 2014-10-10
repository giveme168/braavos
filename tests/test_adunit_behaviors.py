# -*- coding: utf-8 -*-
from pytest_bdd import scenario, given, when, then
from models.medium import AdPosition
from helper import add_unit, add_position, add_medium, get_medium_by_name, get_unit
from .test_consts import TEST_POSITION, TEST_UNIT, TEST_MEDIUM


@scenario('adunit_behaviors.feature', 'query the positions belong to the same medium of the unit')
def test_schedule_behaviros():
    pass


@given('there is a medium called test_medium')
def init_medium(session):
    add_medium(TEST_MEDIUM)


@given('there is a position called test_position and a unit called test_unit. They belong to the medium')
def init_position_and_unit(session):
    medium = get_medium_by_name(TEST_MEDIUM)
    add_unit(TEST_UNIT, 300, medium)
    add_position(TEST_POSITION, medium)


@when('there is one more position')
def init_extra_unit(session):
    add_position('extra_unit')


@then('the count of positions belong to the same medium with the position should be 1')
def get_units_by_medium(session):
    unit = get_unit(TEST_UNIT)
    positions = AdPosition.query.filter_by(medium_id=unit.medium_id)
    assert positions.count() == 1
    assert positions.first().name == TEST_POSITION
