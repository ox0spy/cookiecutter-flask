# -*- coding: utf-8 -*-

import json

from flask_script import Manager, Server
from flask_migrate import MigrateCommand

from {{cookiecutter.app_name}}.extensions import wechat_client, db
from {{cookiecutter.app_name}}.main import app_factory

manager = Manager(app_factory)


def pretty_print(data):
    print(json.dumps(data, indent=4, ensure_ascii=False))


@manager.command
def create_all():
    db.create_all()


@manager.command
def drop_all():
    db.drop_all()


@manager.command
def create_menu():
    pretty_print(wechat_client.create_menu(manager.app.config['WECHAT_MENU']))


@manager.command
def get_menu():
    pretty_print(wechat_client.get_menu())


if __name__ == "__main__":
    server = Server(host="localhost", port=12345)
    manager.add_command("runserver", server)
    manager.add_command("db", MigrateCommand)
    manager.run()
