# -*- coding: utf-8 -*-
from {{cookiecutter.app_name}}.extensions import db


class ModelMixin:
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
    }
    # pylint: disable=no-member
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    def __str__(self):
        return self.__repr__()

    @property
    def columns(self):
        return [c.name for c in self.__table__.columns]
