from helper import add_user, add_order


def test_order(session):
    order = add_order()
    user2 = add_user('testuser2', '2')

    msg = "test comment \n text \n"
    order.add_comment(user2, msg)

    comments = order.get_comments()
    assert comments.count() > 0
    assert comments[0].msg == msg

    comments[0].delete()

    assert order.get_comments().count() == 0
