# -*- coding: utf-8 -*-
from werobot.client import ClientException


class InvalidCommand(Exception):
    def __init__(self, msg):
        super(InvalidCommand, self).__init__(msg)
        self.msg = msg


class AccessTokenInvalid(ClientException):
    pass


class OpenIDInvalid(ClientException):
    pass


class ResponseOutOfTimeLimitOrSubscriptionIsCancel(ClientException):
    pass
