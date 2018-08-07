# -*- coding: utf-8 -*-
from functools import wraps
from flask import request, g, abort

from {{cookiecutter.app_name}}.models.user import User


def no_authenticated(func):
    func.authenticated = False
    return func


def authenticate(func):
    @wraps(func)
    # pylint: disable=inconsistent-return-statements
    def wrapper(*args, **kwargs):
        if not getattr(func, 'authenticated', True):
            return func(*args, **kwargs)
        token = request.cookies.get('token', None)
        if token:
            user_model = User.verify_auth_token(token)
            if user_model:
                g.user_model = user_model
                return func(*args, **kwargs)
        abort(401)

    return wrapper
