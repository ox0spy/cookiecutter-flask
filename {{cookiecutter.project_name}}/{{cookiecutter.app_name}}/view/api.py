from datetime import datetime

from flask import (
    Blueprint, current_app, g, request, jsonify, session,
    redirect, send_from_directory, abort
)

from {{cookiecutter.app_name}} import wechat
from {{cookiecutter.app_name}}.decorators import no_authenticated
from {{cookiecutter.app_name}}.extensions import wechat_client
from {{cookiecutter.app_name}}.models import dba
from {{cookiecutter.app_name}}.models.user import User


api_bp = Blueprint('api', __name__)


@api_bp.route('/openid')
@wechat_client.sns_openid
def get_sns_openid():
    return jsonify(
        openid=g.get('openid', None),
        state=request.args.get('state', None),
    )


@api_bp.route('/userinfo')
@wechat_client.sns_user_info
def get_sns_user_info():
    return jsonify(
        user_info=g.get('user_info', None),
    )


@api_bp.route('/subscribe')
@wechat_client.subscribe_required()
def subscribe():
    """subscribe"""
    return jsonify(
        openid=g.get('openid', None),
    )


@api_bp.route('/jssdk')
def jssdk_config():
    """return js-sdk config"""
    url = request.args.get('url')
    ticket = wechat_client.get_jsapi_ticket()
    sign = wechat.get_signature(ticket, url)
    sign['appid'] = current_app.config['WECHAT_APP_ID']
    return jsonify(sign)


@api_bp.route('/token', methods=['GET'])
@no_authenticated
@wechat_client.subscribe_required()
def get_token():
    dba.add_or_update_user(g.user_info)
    redirect_uri = request.args.get('redirect_uri')
    session['openid'] = g.user_info.get('openid')
    return redirect(redirect_uri)


@api_bp.route('/dump/<table_name>', methods=['GET'])
def dump_table(table_name):
    # 权限检查
    openid = request.args.get('openid', None)
    if not openid or openid not in current_app.config['ADMIN_LIST']:
        return abort(401)

    if table_name == 'user':
        table = User
    else:
        return abort(400)

    filename = '{}-{}.csv'.format(
        table_name, datetime.now().strftime('%Y-%m-%d-%H%M%S')
    )
    dba.dump_table(table, filename)
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True
    )
