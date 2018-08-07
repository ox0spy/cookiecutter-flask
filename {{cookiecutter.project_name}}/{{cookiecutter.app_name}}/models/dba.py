# -*- coding: utf-8 -*-
import csv

from {{cookiecutter.app_name}}.extensions import db, wechat_client
from {{cookiecutter.app_name}}.models.user import User
from {{cookiecutter.app_name}}.config import conf


def user_authentication(identity, token):
    return bool(User.query.filter_by(identity=identity, token=token).first())


def get_identity(openid):
    user = get_or_add_user(openid)
    return {
        "identity": user.identity,
        "user_id": user.id
    }


def get_user_by_identity(identity):
    return User.query.filter_by(identity=identity).first()


def get_user_by_openid(openid):
    return User.query.filter_by(openid=openid).first()


def get_user_by_id(user_id):
    return User.query.filter_by(id=user_id).first()


def get_or_add_user(openid):
    user = get_user_by_openid(openid)
    if not user:
        user_info = wechat_client.get_user_info(openid)
        user = add_user(user_info)
    return user


def set_headimgurl_size(headimgurl, size=64):
    if headimgurl and headimgurl.endswith('/0'):
        return headimgurl.replace('/0', '/%s' % size, -1)
    return headimgurl


def add_user(user_info):
    user_info['headimgurl'] = set_headimgurl_size(
        user_info.get('headimgurl', None)
    )
    user = User(**user_info)
    # pylint: disable=no-member
    db.session.add(user)
    # pylint: disable=no-member
    db.session.commit()
    return user


def add_or_update_user(user_info, openid=None):
    openid = openid or user_info.get('openid', None)
    assert openid is not None
    user = get_user_by_openid(openid)
    if user:
        return update_user(user, user_info)
    return add_user(user_info)


def update_user(user_or_openid, user_info):
    if 'headimgurl' in user_info:
        user_info['headimgurl'] = set_headimgurl_size(
            user_info.get('headimgurl', None)
        )
    if isinstance(user_or_openid, str):
        user = get_user_by_openid(openid=user_or_openid)
    else:
        user = user_or_openid

    for key, value in user_info.items():
        if hasattr(user, key):
            setattr(user, key, value)
    # pylint: disable=no-member
    db.session.commit()
    return user


def dump_table(table, filename):
    save_dir = conf.UPLOAD_FOLDER
    filepath = '{}/{}'.format(save_dir, filename)
    records = table.query.all()
    header = [column.name for column in table.__mapper__.columns]
    with open(filepath, 'w') as fd:
        outcsv = csv.writer(fd)
        outcsv.writerow(header)
        for row in records:
            outcsv.writerow([getattr(row, name) for name in header])

    return filename
