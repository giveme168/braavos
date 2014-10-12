# -*- coding: utf-8 -*-
from pytest_bdd import scenario, given, when, then
from helper import add_unit, add_position, add_medium, add_size, get_medium_by_name, get_position
from .test_consts import TEST_POSITION, TEST_UNIT, TEST_MEDIUM


@scenario('adposition_behaviors.feature', 'query the units from a position')
def test_schedule_behaviros():
    pass


@given('there is a medium called test_medium')
def init_medium(session):
    add_medium(TEST_MEDIUM)


@given('there is a position called and a unit. They belong to the medium and sizes are the same(200, 50)')
def init_position_and_unit(session):
    medium = get_medium_by_name(TEST_MEDIUM)

    size = add_size(200, 50)

    add_unit(TEST_UNIT, 300, medium, size)
    add_position(TEST_POSITION, medium, size)


@when('there is two more units. One is in the same medium and default size')
def init_extra_unit_with_same_medium(session):
    medium = get_medium_by_name(TEST_MEDIUM)

    add_unit('extra_unit', 300, medium)


@when('The other is in the same size with default medium')
def init_extra_unit_with_same_size(session):
    add_unit('extra_unit_1', 300, None, add_size(200, 50))


@then('the count of units belong to the same medium with the position is 1')
def get_units_by_medium(session):
    position = get_position(TEST_POSITION)
    units = position.suitable_units
    assert units.count() == 1
    assert units.first().name == TEST_UNIT
