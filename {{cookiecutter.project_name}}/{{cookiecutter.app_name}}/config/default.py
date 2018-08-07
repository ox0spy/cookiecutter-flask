# -*- coding: utf-8 -*-
import os

PROJECT_NAME = '{{cookiecutter.app_name}}'
# SERVER_NAME = ''
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DEBUG = True
# os.urandom(24)
SECRET_KEY = b''
UPLOAD_FOLDER = '/tmp/'

# log
LOG_LEVEL = 'DEBUG'
LOG_DIR = '/tmp/'
LOGGER_NAME = PROJECT_NAME

# 服务号信息
WECHAT_APP_ID = ''
WECHAT_APP_SECRET = ''
WECHAT_TOKEN = ''
# WECHAT_SESSION_STORAGE = None
WECHAT_ENCODING_AES_KEY = None
WECHAT_ACCESS_TOKEN_KEY = 'wechat:access_token:{{cookiecutter.app_name}}'
WECHAT_JSAPI_TICKET_KEY = 'wechat:jsapi_ticket:{{cookiecutter.app_name}}'

# werobot uri prefix
WEROBOT_URI_PREFIX = '/wechat'
SUBSCRIBE_URL = ''

# 下发给用户的token
TOKEN_MAX_AGE = 60 * 60

# redis
WEROBOT_SESSION_KEY = 'wechat:session:{{cookiecutter.app_name}}'

# cache
CACHE_TYPE = 'redis'
CACHE_DEFAULT_TIMEOUT = 600  # 单位秒
CACHE_KEY_PREFIX = "cache:{{cookiecutter.app_name}}"

# db
SQLALCHEMY_DATABASE_URI = 'sqlite:////{}/{{cookiecutter.app_name}}.sqlite'.format(ROOT_DIR)
SQLALCHEMY_TRACK_MODIFICATIONS = True

# 公众号菜单
WECHAT_MENU = {
    'button': [
        {
            'name': 'test-link',
            'type': 'view',
            'url': 'http://xxx',
        },
        {
            'type': 'click',
            'name': 'test-click',
            'key': 'my-click',
        },
    ]
}

# 关注公众号后获取的用户 openid
ADMIN_LIST = [
    '',
]
