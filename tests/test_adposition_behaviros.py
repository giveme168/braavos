# -*- coding: utf-8 -*-
from pytest_bdd import scenario, given, when, then
from models.medium import AdUnit
from helper import add_unit, add_position, get_position, add_medium, get_medium_by_name
from .test_consts import TEST_POSITION, TEST_UNIT, TEST_MEDIUM


@scenario('adposition_behaviors.feature', 'query the units from a position')
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


@when('there is one more unit')
def init_extra_unit(session):
    add_unit('extra_unit', 300)


@then('the count of units belong to the same medium with the position is 1')
def get_units_by_medium(session):
    position = get_position(TEST_POSITION)
    units = AdUnit.query.filter_by(medium_id=position.medium_id)
    assert units.count() == 1
    assert units.first().name == TEST_UNIT
