# encoding: utf-8
import sys
import datetime
# sys.path.append('/Users/guoyu1/workspace/inad/braavos')
sys.path.append('/home/inad/apps/braavos/releases/current')

from app import app

from controllers.account.onduty import _get_last_onduty_date, _get_last_week_date, _format_out, _format_leave, _format_onduty, _get_onduty
from models.user import User
from libs.mail import send_html_mail


if __name__ == '__main__':
    start_date, end_date = _get_last_week_date()
    end_date = end_date + datetime.timedelta(1)
    start_date = datetime.datetime.strptime(
        start_date.strftime('%Y-%m-%d'), '%Y-%m-%d')
    end_date = datetime.datetime.strptime(
        end_date.date().strftime('%Y-%m-%d'), '%Y-%m-%d')
    all_active_user = User.all_active()
    salers = [u for u in all_active_user if u.location == 1 and u.is_out_saler]
    outs = _format_out()
    leaves = _format_leave()
    all_dus = _format_onduty(start_date, end_date)
    # 打卡最后一次时间
    last_onduty_date = _get_last_onduty_date()
    users = []
    for user in salers:
        u_outs = [k for k in outs if k['creator_id'] == int(user.id)]
        u_leaves = [k for k in leaves if k['creator_id'] == int(user.id)]
        dutys = _get_onduty(all_dus, u_outs, u_leaves, user,
                            start_date, end_date, last_onduty_date)
        users.append({'count': sum(item['warning_count'] for item in dutys),
                      'user': user})
    unusual_body = ""
    for k in users:
        if k['count'] > 0:
            red = "style='color:red;'"
        else:
            red = ''
        unusual_body += u"""<tr>
            <td>%s</td>
            <td %s >%s</td>
            <td><a href='http://z.inad.com/account/onduty/%s/info?start_time=%s&end_time=%s'>查看</a></td>
        </tr>""" % (k['user'].name, red, str(k['count']), k['user'].id, str(start_date.date()), str(end_date.date()))

    body = u"""
    <h1>%s至%s  华北-销售考勤异常表</h1>
    <table border="1" cellpadding="0" cellspacing="0" style="width:600px;">
        <tr>
            <td>姓名</td>
            <td>异常次数</td>
            <td>操作</td>
        </tr>
        %s
    </table>
    <p>详情链接地址: %s<br/>
    由于数据准确性问题，请仔细核对是否准确，如果有问题请找郭钰。
    </p>
    """ % (str(start_date.date()), str(end_date.date()), unusual_body, 'http://z.inad.com/account/onduty/unusual')
    send_html_mail(u'华北-销售考勤异常表',
                   recipients=['guoyu@inad.com', 'lixuezhi@inad.com', 'shiying@inad.com',
                               'yangqian@inad.com', 'yanyue@inad.com', 'weizhaoting@inad.com', 'huawei@inad.com'],
                   body=body)
