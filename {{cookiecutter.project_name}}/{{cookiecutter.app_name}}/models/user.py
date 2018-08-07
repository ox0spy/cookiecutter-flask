# pylint: disable=no-member
import uuid
import enum
from datetime import datetime

from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer, SignatureExpired, BadSignature

from {{cookiecutter.app_name}}.extensions import db
from {{cookiecutter.app_name}}.models import ModelMixin


class GenderEnum(enum.IntEnum):
    """gender enum"""

    unknown = 0
    male = 1
    female = 2


class User(db.Model, ModelMixin):
    """User Model"""

    def _uuid():  # pylint: disable=no-method-argument
        return uuid.uuid4().hex

    __tablename__ = 'user'
    openid = db.Column(
        db.String(50),
        unique=True, index=True, doc='用户的标识，对当前公众号唯一'
    )
    identity = db.Column(
        db.String(40),
        default=_uuid, unique=True, index=True, doc="用户身份标识"
    )

    nickname = db.Column(db.String(50), nullable=False, doc='用户的昵称')
    gender = db.Column(
        db.Enum(GenderEnum),
        nullable=False,
        doc='用户的性别，值为1时是男性，值为2时是女性，值为0时是未知'
    )
    city = db.Column(db.String(50), nullable=False, doc='用户所在城市')
    country = db.Column(db.String(50), nullable=False, doc='用户所在国家')
    province = db.Column(db.String(50), nullable=False, doc='省份')
    language = db.Column(
        db.String(50),
        nullable=False, doc='用户的语言，简体中文为zh_CN'
    )
    headimgurl = db.Column(
        db.String(260), nullable=True,
        doc=('用户头像，最后一个数值代表正方形头像大小'
             '（有0、46、64、96、132数值可选，0代表640*640正方形头像），'
             '用户没有头像时该项为空。若用户更换头像，原有头像URL将失效。'
             )
    )
    subscribe_time = db.Column(
        db.Integer, nullable=False,
        doc='用户关注时间，为时间戳。如果用户曾多次关注，则取最后关注时间',
        index=True
    )
    unionid = db.Column(
        db.String(50),
        nullable=True,
        doc='只有在用户将公众号绑定到微信开放平台帐号后，才会出现该字段'
    )
    remark = db.Column(
        db.String(50),
        nullable=True,
        doc='公众号运营者对粉丝的备注，运营者可在用户管理界面添加备注'
    )
    groupid = db.Column(
        db.Integer, nullable=True, doc='用户所在的分组ID'
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.now, index=True, doc='用户信息创建时间'
    )
    updated_at = db.Column(
        db.DateTime,
        onupdate=datetime.now, doc='用户信息最近更新时间'
    )

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self):
        return '<User("{}", "{}", "{}")>'.format(
            self.id, self.openid, self.nickname
        )

    @property
    def gender(self):  # pylint: disable=function-redefined
        if self.gender == GenderEnum.male:
            return "男"

        if self.gender == GenderEnum.female:
            return "女"

        return "未知"

    def generate_auth_token(self):
        s = TimedJSONWebSignatureSerializer(
            current_app.config['SECRET_KEY'],
            expires_in=current_app.config.get('TOKEN_MAX_AGE')
        )
        return s.dumps({'identity': self.identity})

    @staticmethod
    def verify_auth_token(token):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        return User.query.filter_by(identity=data['identity']).first()
