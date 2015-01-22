from models.user import User
from config import DEFAULT_PASSWORD
from helper import add_user


def test_add_user(session):
    user = add_user('testuser1', DEFAULT_PASSWORD)

    user2 = User.get_by_email('testuser1@inad.com')
    assert user2.id == user.id
    assert user2.email == user.email
    assert user2.check_password(DEFAULT_PASSWORD)


def test_update_user(session):
    user = add_user('testuser1', DEFAULT_PASSWORD)

    assert user.name == 'testuser1'
    assert user.check_password(DEFAULT_PASSWORD)

    user.name = 'testuser2'
    user.set_password('test')

    assert user.name == 'testuser2'
    assert user.check_password('test')


def test_delete_user(session):
    user = add_user('testuser1', DEFAULT_PASSWORD)
    user_id = user.id

    user.delete()
    assert User.get(user_id) is None
