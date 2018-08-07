# -*- coding: utf-8 -*-
import importlib
import logging
import os

from flask import render_template, request, session, redirect, url_for
from werobot.contrib.flask import make_view
from werobot.session.redisstorage import RedisStorage

from {{cookiecutter.app_name}}.config import conf
from {{cookiecutter.app_name}}.view.api import api_bp
from {{cookiecutter.app_name}}.view.page import pages
from {{cookiecutter.app_name}}.view.robot import robot
from .app import Flask
from .extensions import (
    wechat_client, redis_store, db, cors, migrate, cache, scheduler
)


def app_factory(config=None):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    app = Flask(
        __name__,
        static_folder=os.path.join(root_dir, 'static'),
        template_folder=os.path.join(root_dir, 'templates')
    )

    config_app(app, config or conf)
    # redis_store must configured before wechat_client, as it need by wechat_client
    config_redis(app)
    config_logger(app)
    config_blueprints(app)
    config_extensions(app)
    config_werobot(app)
    config_database(app)
    config_request_hooks(app)
    configure_error_handlers(app)
    get_url_map(app)
    # pylint: disable=no-member
    app.logger.info("app started...")
    return app


def get_url_map(app):
    for url in app.url_map.iter_rules():
        print(url)


def config_logger(app, force=False):
    if force or not app.debug:
        stream_format = logging.Formatter(
            '%(asctime)s %(name)s %(levelname)s: %(message)s'
            '[in %(pathname)s:%(lineno)d]'
        )
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(stream_format)
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.INFO)


def config_app(app, config):
    if isinstance(config, str):
        config = importlib.import_module('{{cookiecutter.app_name}}.config.%s' % config)
    app.config.from_object(config)


def config_werobot(app):
    robot.config.update(
        TOKEN=app.config['WECHAT_TOKEN'],
        ENCODING_AES_KEY=app.config['WECHAT_ENCODING_AES_KEY'],
        APP_ID=app.config['WECHAT_APP_ID'],
        SESSION_STORAGE=RedisStorage(
            redis_store, prefix=app.config['WEROBOT_SESSION_KEY']
        ),
    )
    robot.logger = app.logger
    app.add_url_rule(app.config['WEROBOT_URI_PREFIX'],
                     endpoint='werobot',
                     view_func=make_view(robot),
                     methods=['GET', 'POST'])


def config_database(app):
    db.init_app(app)
    db.app = app
    # disable to use db migrate
    # db.create_all()
    migrate.init_app(app, db)


def config_redis(app):
    redis_store.init_app(app)


def config_extensions(app):
    wechat_client.init_app({
        "APP_ID": app.config["WECHAT_APP_ID"],
        "APP_SECRET": app.config["WECHAT_APP_SECRET"],
        "ACCESS_TOKEN_KEY": app.config['WECHAT_ACCESS_TOKEN_KEY'],
        "JSAPI_TICKET_KEY": app.config['WECHAT_JSAPI_TICKET_KEY'],
        "SESSION_STORAGE": RedisStorage(redis_store, prefix=app.config['WEROBOT_SESSION_KEY'])
    })
    if app.debug:
        cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    if not app.debug:
        scheduler.init_app(app)
        scheduler.start()
    cache.init_app(app)


def config_blueprints(app):
    app.register_blueprint(pages, url_prefix='/pages')
    app.register_blueprint(api_bp, url_prefix='/api')


def config_request_hooks(app):
    @app.before_request
    # pylint: disable=too-many-boolean-expressions, unused-variable, inconsistent-return-statements
    def check_token():
        url = request.url
        openid = session.get('openid', None)
        # pylint: disable=too-many-boolean-expressions
        if (
                openid is None and
                request.method == 'GET' and
                request.path != url_for('api.get_token') and
                '/wechat' not in request.path and
                '/pages/' not in request.path and
                '/static/' not in request.path and
                '/dump/' not in request.path
        ):
            return redirect(url_for('api.get_token', redirect_uri=url))


def configure_error_handlers(app):
    @app.errorhandler(403)
    # pylint: disable=unused-argument, unused-variable
    def forbidden_page(error):
        return render_template("error/access_forbidden.html"), 403

    @app.errorhandler(404)
    # pylint: disable=unused-argument, unused-variable
    def page_not_found(error):
        return render_template("error/page_not_found.html"), 404

    @app.errorhandler(405)
    # pylint: disable=unused-argument, unused-variable
    def method_not_allowed_page(error):  # pylint: disable=unused-argument
        return render_template("error/method_not_allowed.html"), 405

    @app.errorhandler(500)
    # pylint: disable=unused-argument, unused-variable
    def server_error_page(error):  # pylint: disable=unused-argument
        return render_template("error/server_error.html"), 500

    @app.errorhandler(410)
    # pylint: disable=unused-argument, unused-variable
    def page_gone(error):  # pylint: disable=unused-argument
        return render_template("error/page_gone.html"), 410
