# coding: utf-8
from pytest_bdd import scenario, given, when, then
from models.user import Team


@scenario('team.feature', 'use name, create team')
def test_team():
    pass


@given('team名字: OneTeam')
def given_team_name():
    pass


@when('创建对应名字的team')
def when_create_team(session):
    Team.add(name='OneTeam')


@then('用这个名字的 1 个team被创建了.')
def then_create_a_team(session):
    assert len(Team.query.filter_by(name='OneTeam').all()) == 1
