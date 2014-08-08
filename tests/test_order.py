from models.order import Order
from helper import add_user, add_order


def test_order(session):
    order = add_order()

    order2 = Order.get(order.id)
    assert order2 is not None

    user2 = add_user('testuser2', 'pwd', '2')

    order.designers = [user2]
    order3 = Order.get(order.id)
    assert user2 in order3.designers
