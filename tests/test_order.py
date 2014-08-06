from datetime import datetime

from models.order import Order
from test_user import _add_user
from test_medium import _add_medium
from test_client import _add_client, _add_agent


def _add_order():
    user = _add_user('testuser', 'pwd', '1')
    medium = _add_medium('testmedium')
    client = _add_client('testclient')
    agent = _add_agent('testagent')
    order = Order(client, 'testcampaign', medium, 0, 'testcontract', 1000, agent,
                  [user], [], [], [], [], user, datetime.now())
    order.add()
    return order


def test_order(session):
    order = _add_order()

    order2 = Order.get(order.id)
    assert order2 is not None

    user2 = _add_user('testuser2', 'pwd', '2')

    order.designers = [user2]
    order3 = Order.get(order.id)
    assert user2 in order3.designers
