# -*- coding: utf-8 -*-
import os

from {{cookiecutter.app_name}}.config import prod, dev, test
from {{cookiecutter.app_name}}.main import app_factory

if os.environ.get('DEPLOY_ENV') == 'prod':
    app = app_factory(prod)
elif os.environ.get('DEPLOY_ENV') == 'test':
    app = app_factory(test)
else:
    app = app_factory(dev)
