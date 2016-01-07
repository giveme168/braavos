# -*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from flask import Blueprint, request, jsonify

from models.user import User
from libs.mail import check_auth_by_mail
from controllers.api.sdk.baidu_push.Channel import Channel
from controllers.api.sdk.baidu_push.lib.ChannelException import ChannelException

api_account_bp = Blueprint('api_account', __name__)


@api_account_bp.route('/login', methods=['GET', 'POST'])
def login():
    is_pwd = request.values.get('is_pwd', '')
    username = request.values.get('username', '')
    password = request.values.get('password', '')
    if is_pwd:
        if check_auth_by_mail(username, password):
            user = User.query.filter_by(email=username).first()
            data = {
                'uid': user.id,
                'name': user.name,
                'email': user.email
            }
            return jsonify({'ret': True, 'data': data})
        else:
            return jsonify({'ret': False, 'msg': u'用户名或密码不正确'})
    else:
        user = User.get_by_email(email=username.lower())
        if user and user.check_password(password):
            data = {
                'uid': user.id,
                'name': user.name,
                'email': user.email
            }
            return jsonify({'ret': True, 'data': data})
        else:
            return jsonify({'ret': False, 'msg': u'用户名或密码不正确'})
    return jsonify({'ret': False})


@api_account_bp.route('/<uid>/band_channel_id', methods=['GET', 'POST'])
def band_channel_id(uid):
    channel_id = request.values.get('channel_id', '')
    device_type = int(request.values.get('device_type', 4))

    msg = u'{"title":"绑定channel_id","description":"channel_id为:%s"}' % (
        channel_id)
    # msg_ios = '{"aps":{"alert":"iOS Message from Push","sound":"","badge":1},"key1":"value1","key2":"value2"}'
    opts = {'msg_type': 1, 'expires': 300}
    c = Channel()
    c.setDeviceType(device_type)
    try:
        ret = c.pushMsgToSingleDevice(str(channel_id), str(msg), opts)
        print ret
    except ChannelException as e:
        print '[code]: %s [msg]: %s [request id]: %s' % (e.getLastErrorCode(), e.getLastErrorMsg(), c.getRequestId())
    return jsonify({'ret': True})
