# -*- coding: utf-8 -*-
import json
from functools import wraps
import os

import flask
from flask import request, current_app
import flask.testing
import werobot

from {{cookiecutter.app_name}}.models.dba import get_identity


class Request(flask.Request):  # pylint: disable=too-many-ancestors
    def on_json_loading_failed(self, e):
        msg = os.linesep.join([
            'Bad Request INFO:',
            'request path: {}'.format(request.path),
            'request method: {}'.format(request.method),
            'request value: {}'.format(request.values),
            'request data: {}'.format(request.data),
            'request headers: {}'.format(request.headers),
        ])
        current_app.logger.error(msg)
        super(Request, self).on_json_loading_failed(e)

    def to_json(self, pretty=True):
        indent = 4 if pretty else None
        return json.dumps({
            'method': self.method,
            'path': self.path,
            'args': self.args.to_dict(False) if self.args else None,
            'json': self.json or None,
            'data': self.data.decode('utf-8'),
            'values': self.values.to_dict(False)
        }, indent=indent)

    def to_dict(self):
        return {'request_info': self.to_json()}


class FlaskClient(flask.testing.FlaskClient):
    def post_json(self, *args, **kw):
        kw['content_type'] = 'application/json'
        if 'data' in kw and isinstance(kw['data'], dict):
            kw['data'] = json.dumps(kw['data'])
        return self.post(*args, **kw)

    def put_json(self, *args, **kw):
        kw['content_type'] = 'application/json'
        if 'data' in kw and isinstance(kw['data'], dict):
            kw['data'] = json.dumps(kw['data'])
        return self.put(*args, **kw)


class Flask(flask.Flask):
    test_client_class = FlaskClient
    request_class = Request

    def log_exception(self, exc_info):
        # pylint: disable=no-member
        self.logger.error(
            'ERROR Request INFO: {}'.format(request.to_json(pretty=True)),
            exc_info=exc_info,
            extra=request.to_dict())

    @property
    def in_debug_env(self):
        return self.config['CONFIG_NAME'] != 'prod'


class WeRoBot(werobot.WeRoBot):
    def identity(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            message = args[0] if args else None
            if message:
                user = get_identity(message.source)
                setattr(message, 'identity', user['identity'])
                setattr(message, 'user_id', user['user_id'])
            return func(*args, **kwargs)

        return wrapper
