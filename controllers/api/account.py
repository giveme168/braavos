# -*- coding: UTF-8 -*-
import sys
import datetime
reload(sys)
sys.setdefaultencoding('utf8')
from flask import Blueprint, request, jsonify

from models.user import User, UserOnDuty, Leave, LEAVE_TYPE_CN
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

    msg = u'{"title":"绑定channel_id","description":"channel_id为:%s", "custom_content":{"channel_id":%s}}' % (
        channel_id, channel_id)
    # msg_ios = '{"aps":{"alert":"iOS Message from
    # Push","sound":"","badge":1},"key1":"value1","key2":"value2"}'
    opts = {'msg_type': 1, 'expires': 300}
    c = Channel()
    c.setDeviceType(device_type)
    try:
        ret = c.pushMsgToSingleDevice(str(channel_id), str(msg), opts)
        print ret
        return jsonify({'ret': True, 'data': {'uid': uid, 'channel_id': channel_id}})
    except ChannelException as e:
        msg = '[code]: %s [msg]: %s [request id]: %s' % (
            e.getLastErrorCode(), e.getLastErrorMsg(), c.getRequestId())
        return jsonify({'ret': False, 'msg': msg})
    return jsonify({'ret': False, 'msg': 'method error'})


@api_account_bp.route('/<uid>/onduty/create', methods=['GET', 'POST'])
def onduty_create(uid):
    # channel_id = request.values.get('channel_id', '')
    try:
        user = User.get(uid)
    except:
        return jsonify({'ret': False, 'msg': u'用户找不到'})
    onduty = UserOnDuty.add(user=user,
                            sn=user.sn,
                            check_time=datetime.datetime.now(),
                            create_time=datetime.datetime.now(),
                            type=1)
    return jsonify({'ret': True,
                    'data': {'uid': user.id,
                             'check_time': onduty.check_time.strftime('%Y-%m-%d %H:%M:%S')
                             }
                    })


@api_account_bp.route('/<uid>/leave/create', methods=['GET', 'POST'])
def leave_create(uid):
    try:
        user = User.get(uid)
    except:
        return jsonify({'ret': False, 'msg': u'用户找不到'})
    if request.method == 'POST':
        try:
            type = int(request.values.get('type', 1))
        except:
            return jsonify({'ret': False, 'msg': u'请假类型错误'})

        try:
            start_time = datetime.datetime.strptime(
                request.values.get('start'), '%Y-%m-%d %H'),
            end_time = datetime.datetime.strptime(
                request.values.get('end'), '%Y-%m-%d %H'),
        except:
            return jsonify({'ret': False, 'msg': u'开始结束时间错误'})
        day = request.values.get('day', '0')
        half = request.values.get('half', '1')
        reason = request.values.get('reason', '')
        senders_ids = request.values.get('senders', '').split('|')
        try:
            senders = User.gets(senders_ids)
        except:
            return jsonify({'ret': False, 'msg': u'抄送人错误'})
        leave = Leave.add(type=type,
                          start_time=start_time,
                          end_time=end_time,
                          rate_day=day + '-' + half,
                          reason=reason,
                          status=1,
                          senders=senders,
                          creator=user,
                          create_time=datetime.date.today())
        return jsonify({'ret': True,
                        'data': {'uid': user.id,
                                 'start_time': leave.start_time.strftime('%Y-%m-%d %H'),
                                 'end_time': leave.end_time.strftime('%Y-%m-%d %H'),
                                 }
                        })
    days = [{'key': k, 'value': k} for k in range(0, 21)]
    days += [{'key': k, 'value': k} for k in [30, 98, 113, 128]]
    return jsonify({'ret': True, 'data': {
        'type': [{'key': k[0], 'value': k[1]}for k in LEAVE_TYPE_CN.items()],
        'day': days,
        'half': [{'key': '0', 'value': u'整'},
                 {'key': '1', 'value': u'上半天'},
                 {'key': '2', 'value': u'下半天'}],
        'senders': [{'id': m.id, 'name': m.name} for m in User.all_active()],
        'default': u"%s，admin@inad.com（请假时长大于等于5天由黄亮审批）" % (user.team_leaders_cn)
    }
    })


@api_account_bp.route('/<uid>/leave/index', methods=['GET'])
def leave_index(uid):
    leaves = [k for k in Leave.all() if k.creator.id == int(uid)]
    data = []
    for k in leaves:
        param = {}
        param['type'] = k.type
        param['type_cn'] = k.type_cn
        param['start_time'] = k.start_time.strftime('%Y-%m-%d %H')
        param['end_time'] = k.end_time.strftime('%Y-%m-%d %H')
        param['day'] = k.rate_day.split('-')[0]
        param['day_cn'] = param['day'] + u'天'
        param['half'] = k.rate_day.split('-')[1]
        param['half_cn'] = k.half_cn
        param['senders'] = [{'id': m.id, 'name': m.name} for m in k.senders]
        param['reason'] = k.reason
        param['status'] = k.status
        param['status_cn'] = k.status_cn
        data.append(param)
    return jsonify({'ret': True, 'data': data})
