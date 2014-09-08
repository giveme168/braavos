# -*- coding: UTF-8 -*-
from flask import g, abort
from functools import wraps


def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if g.user and g.user.team.is_admin():
            return func(*args, **kwargs)
        return abort(401)
    return decorated_view


def admin_required_before_request():
    if not g.user or not g.user.team.is_admin():
        return abort(401)
