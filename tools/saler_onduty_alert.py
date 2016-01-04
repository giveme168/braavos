# encoding: utf-8
import sys
sys.path.append('/Users/guoyu1/workspace/inad/braavos')
# sys.path.append('/home/inad/apps/braavos/releases/current')

from app import app

from controllers.account.onduty import _get_last_week_date, _get_unusual
from libs.mail import send_html_mail


if __name__ == '__main__':
    start_date, end_date = _get_last_week_date()
    users = _get_unusual(start_date, end_date)
    unusual_body = ""
    for k in users:
        if k.unusual_count > 0:
            red = "style='color:red;'"
        else:
            red = ''
        unusual_body += u"""<tr>
            <td>%s</td>
            <td %s >%s</td>
            <td><a href='http://z.inad.com/account/onduty/%s/info?start_time=%s&end_time=%s'>查看</a></td>
        </tr>""" % (k.name, red, str(k.unusual_count), k.id, str(start_date), str(end_date))

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
    """ % (str(start_date), str(end_date), unusual_body, 'http://z.inad.com/account/onduty/unusual')
    send_html_mail(u'华北-销售考勤异常表', recipients=['guoyu@inad.com'], body=body)
