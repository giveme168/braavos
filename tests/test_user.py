from models.user import User, Team
from config import DEFAULT_PASSWORD


def _add_team(name):
    team = Team(name=name)
    team.add()
    return team


def _add_user(name, pwd, phone='1234567'):
    team = _add_team('testteam1')
    user = User(name=name, email=(name + '@inad.com'),
                password=pwd, phone=phone, team=team)
    user.add()
    return user


def test_add_user(session):
    user = _add_user('testuser1', DEFAULT_PASSWORD)

    user2 = User.get_by_email('testuser1@inad.com')
    assert user2.id == user.id
    assert user2.email == user.email
    assert user2.check_password(DEFAULT_PASSWORD)


def test_update_user(session):
    user = _add_user('testuser1', DEFAULT_PASSWORD)

    assert user.name == 'testuser1'
    assert user.check_password(DEFAULT_PASSWORD)

    user.name = 'testuser2'
    user.set_password('test')

    assert user.name == 'testuser2'
    assert user.check_password('test')


def test_delete_user(session):
    user = _add_user('testuser1', DEFAULT_PASSWORD)
    user_id = user.id

    user.delete()
    assert User.get(user_id) is None
