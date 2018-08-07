"""extensions module"""
# -*- coding: utf-8 -*-
from flask_apscheduler import APScheduler
from flask_cors import CORS
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_migrate import Migrate

from .wechat import WeChatClientWithFlask

wechat_client = WeChatClientWithFlask()
redis_store = FlaskRedis()
db = SQLAlchemy()
cache = Cache()
cors = CORS()
migrate = Migrate()
scheduler = APScheduler()
