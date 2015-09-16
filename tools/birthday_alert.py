# encoding: utf-8
import os
import datetime
import sys
#sys.path.append('/Users/guoyu1/workspace/inad/braavos') 
sys.path.append('/home/inad/apps/braavos/releases/current') 

from app import app

from models.user import User
from libs.mail import send_html_mail




def get_all_today_is_birthday(name, email):
    text = u"""
    <div class="container-fluid" tabindex="-1" style="background-image:url(http://z.inad.com/static/imgs/brithday_1.jpg);background-repeat: no-repeat; background-position: center 0;min-height:660px;width:700px;position: relative;">
      <div style="position:absolute;left:38%%;top:18%%;color:#FF44AA; font-family:Microsoft YaHei;width:360px;font-size:20px;">
        <h3 >%s ：</h3>
      <div>
    </div>

    <br/><br/>
    """%(name)
    to_emails = [email]
    try:
        send_html_mail(u'生日快乐！', recipients=to_emails, body=text)
    except:
        pass

if __name__ == '__main__':
    now_date = datetime.datetime.now().strftime('%m%d')
    users = User.all_active()
    for k in users:
        try:
            birthday = k.birthday.strftime('%m%d')
            ini_birthday = k.birthday.strftime('%Y%m%d')
            if ini_birthday != '19700101':
                if birthday == now_date:
                    get_all_today_is_birthday(k.name, k.email)
        except:
            pass
