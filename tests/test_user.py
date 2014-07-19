from braavos.models.user import User, Team
from braavos.config import DEFAULT_PASSWORD


def test_hello():
    assert 1 == 1


def test_create_user(session):
    team1 = Team(name='testteam1')
    user1 = User(name='testuser1', email='testuser1@inad.com',
                 password=DEFAULT_PASSWORD, phone='111111', team=team1)
    user1.add()
    users = User.all()
    assert len(users) == 1
