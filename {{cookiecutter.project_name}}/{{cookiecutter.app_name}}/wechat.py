"""weixin module"""
# -*- coding: utf-8 -*-
import hashlib
import time
import json
from functools import wraps

import requests
from flask import (redirect, request, g, current_app)
from retrying import retry
import werobot

from {{cookiecutter.app_name}}.exceptions import (
    AccessTokenInvalid, OpenIDInvalid,
    ResponseOutOfTimeLimitOrSubscriptionIsCancel
)
from {{cookiecutter.app_name}}.libs.utils import get_random_string


def get_signature(jsapi_ticket, url):
    """jsapi_ticket 签名"""
    sign = {
        'noncestr': get_random_string(15, True),
        'jsapi_ticket': jsapi_ticket,
        'timestamp': int(time.time()),
        'url': url
    }
    signature = '&'.join(['%s=%s' % (key.lower(), sign[key]) for key in sorted(sign)])
    sign["signature"] = hashlib.sha1(signature.encode('utf-8')).hexdigest()
    sign.pop('jsapi_ticket')
    return sign


def check_error(data):
    """
    检测微信公众平台返回值中是否包含错误的返回码。
    如果返回码提示有错误，抛出一个 :class:`ClientException` 异常。对于AccessToken失效的异常单独抛出，便于重试。
    """
    if "errcode" in data and data["errcode"] != 0:
        if data['errcode'] == 40001:
            raise AccessTokenInvalid(
                "{}: {}".format(data["errcode"], data["errmsg"])
            )
        if data['errcode'] == 40003:
            raise OpenIDInvalid(
                "{}: {}".format(data["errcode"], data["errmsg"])
            )
        if data['errcode'] == 45015:
            raise ResponseOutOfTimeLimitOrSubscriptionIsCancel(
                "{}: {}".format(data["errcode"], data["errmsg"])
            )
        raise werobot.client.ClientException(
            "{}: {}".format(data["errcode"], data["errmsg"])
        )
    return data


def retry_exception(exception):
    """retry on exception"""
    return isinstance(
        exception,
        (
            AccessTokenInvalid,
            requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectTimeout,
            # pylint: disable=no-member
            requests.packages.urllib3.exceptions.ConnectTimeoutError,
            # pylint: disable=no-member
            requests.packages.urllib3.exceptions.ReadTimeoutError,
        )
    )


class WeChatClientWithFlask(werobot.client.Client):
    # pylint: disable=too-many-public-methods
    SNSAPI_BASE_SCOPE = 'snsapi_base'
    SNSAPI_USERINFO_SCOPE = 'snsapi_userinfo'

    def __init__(self, config=None):
        if config is None:
            config = {}
        super(WeChatClientWithFlask, self).__init__(config)

    def init_app(self, config):
        self.config = werobot.config.Config(dict(
            APP_ID=config.get("APP_ID", None),
            APP_SECRET=config.get("APP_SECRET", None),
            ACCESS_TOKEN_KEY=config.get('ACCESS_TOKEN_KEY', None),
            JSAPI_TICKET_KEY=config.get('JSAPI_TICKET_KEY', None),
            SESSION_STORAGE=config.get('SESSION_STORAGE', None),
        ))

    @property
    def access_token_key(self):
        return self.config.get('ACCESS_TOKEN_KEY')

    @property
    def session_storage(self):
        return self.config.get('JSAPI_TICKET_KEY')

    @property
    def jsapi_ticket_key(self):
        return self.config.get('SESSION_STORAGE')

    def _get_access_token(self, force=False):
        from {{cookiecutter.app_name}}.extensions import redis_store
        access_token = redis_store.get(self.access_token_key)
        if force or not access_token:
            data = self.grant_token()
            access_token = data["access_token"]
            redis_store.set(self.access_token_key, access_token)
            # 设置有效期比实际有效期短2分钟，减少误差
            redis_store.expire(self.access_token_key, data["expires_in"] - 120)
        return access_token

    def get_access_token(self):
        return self._get_access_token()

    @retry(stop_max_attempt_number=3, retry_on_exception=retry_exception)
    # pylint: disable=inconsistent-return-statements
    def request(self, method, url, **kwargs):
        if "params" not in kwargs:
            kwargs["params"] = {"access_token": self.token}
        elif (
                "access_token" in kwargs["params"] and
                not kwargs.pop('is_authorize_access_token', False)
        ):
            kwargs["params"]["access_token"] = self.token

        if isinstance(kwargs.get("data", ""), dict):
            body = json.dumps(kwargs["data"], ensure_ascii=False)
            body = body.encode('utf8')
            kwargs["data"] = body
        req = requests.request(
            method=method,
            url=url,
            timeout=5,
            **kwargs
        )
        req.raise_for_status()
        data = req.json()
        try:
            if check_error(data):
                return data
        except AccessTokenInvalid as e:
            self._get_access_token(force=True)
            raise e

    def get_authorize_code_url(self, scope, redirect_uri, state=""):
        params = (
            ("appid", self.appid),
            ("redirect_uri", redirect_uri),
            ("response_type", "code"),
            ("scope", scope),
            ("state", state)
        )
        req = requests.Request(
            method='GET',
            url='https://open.weixin.qq.com/connect/oauth2/authorize#wechat_redirect',
            params=params
        )
        return req.prepare().url

    def get_authorize_access_token_by_code(self, authorize_code):
        return self.get('https://api.weixin.qq.com/sns/oauth2/access_token', params={
            'appid': self.appid,
            'secret': self.appsecret,
            'code': authorize_code,
            'grant_type': 'authorization_code'

        })

    def get_sns_user_info(self, authorize_access_token, openid, lang='zh_CN'):
        return self.get(
            'https://api.weixin.qq.com/sns/userinfo',
            params={
                'access_token': authorize_access_token,
                'openid': openid,
                'lang': lang,
            },
            is_authorize_access_token=True,
        )

    def sns_openid(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            code = request.args.get('code', None)
            if not code:
                return redirect(
                    self.get_authorize_code_url(
                        WeChatClientWithFlask.SNSAPI_BASE_SCOPE,
                        request.url
                    )
                )
            access_token_info = self.get_authorize_access_token_by_code(code)
            g.openid = access_token_info.get('openid', None)
            g.access_token = access_token_info.get('access_token', None)
            return func(*args, **kwargs)

        return wrapper

    def subscribe_required(self, subscribe_url=None):
        def decorator(func):
            @self.sns_openid
            @wraps(func)
            def wrapper(*args, **kwargs):
                g.user_info = self.get_user_info(g.openid)
                if g.user_info['subscribe'] == 1:
                    return func(*args, **kwargs)
                return redirect(
                    subscribe_url or current_app.config['SUBSCRIBE_URL']
                )

            return wrapper
        return decorator

    def sns_user_info(self, func):
        @self.sns_openid
        @wraps(func)
        def wrapper(*args, **kwargs):
            g.user_info = self.get_sns_user_info(g.access_token, g.openid)
            return func(*args, **kwargs)

        return wrapper

    # reffer http://mp.weixin.qq.com/wiki/5/6dde9eaa909f83354e0094dc3ad99e05.html
    def set_industry(self, industry_id1, industry_id2):
        return self.post(
            'https://api.weixin.qq.com/cgi-bin/template/api_set_industry',
            data={
                'industry_id1': industry_id1,
                'industry_id2': industry_id2,
            }
        )

    def get_industry(self):
        return self.get(
            'https://api.weixin.qq.com/cgi-bin/template/get_industry'
        )

    def get_all_private_template(self):
        url = 'https://api.weixin.qq.com/cgi-bin/template/get_all_private_template'
        return self.get(url)

    def set_session(self, openid, value):
        session_storage = self.session_storage
        if not session_storage:
            raise KeyError("please set SESSION_STORAGE in init_app")
        if value:
            session_storage[openid] = value

    def get_session(self, openid):
        session_storage = self.session_storage
        if not session_storage:
            raise KeyError("please set SESSION_STORAGE in init_app")
        return session_storage[openid]

    def jsapi_ticket(self):
        return self.get(
            'https://api.weixin.qq.com/cgi-bin/ticket/getticket',
            params={
                'type': 'jsapi',
                'access_token': self.token,
            }
        )

    def get_jsapi_ticket(self, force=False):
        from {{cookiecutter.app_name}}.extensions import redis_store
        ticket = redis_store.get(self.jsapi_ticket_key)
        ticket = ticket.decode('utf-8') if ticket else None
        if force or not ticket:
            data = self.jsapi_ticket()
            ticket = data["ticket"]
            redis_store.set(self.jsapi_ticket_key, ticket)
            # 设置有效期比实际有效期短2分钟，减少误差
            redis_store.expire(self.jsapi_ticket_key, data["expires_in"] - 120)
        return ticket

    def get_image_urls(self):
        return self.post(
            'https://api.weixin.qq.com/cgi-bin/material/batchget_material',
            data={
                "type": "image",
                "offset": 0,
                "count": 20,
            }
        )

    def get_callback_ip(self):
        return self.get("https://api.weixin.qq.com/cgi-bin/getcallbackip")
