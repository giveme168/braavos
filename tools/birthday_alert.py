# encoding: utf-8
import os
import sys
#sys.path.append('/Users/guoyu1/workspace/inad/braavos') 
sys.path.append('/home/inad/apps/braavos/releases/current') 
from app import app
from models.user import User
from libs.mail import send_html_mail




def get_all_today_is_birthday():
    text = u"""
    <div class="container-fluid" tabindex="-1" style="background-image:url(http://z.inad.com/static/imgs/brithday.jpg);background-repeat: no-repeat; background-position: center 0;min-height:660px;width:700px;position: relative;">
      <div style="position:absolute;left:25%%;top:20%%;color:#FF44AA; font-family:Microsoft YaHei;width:370px;">
        <h3 >亲爱的 %s ：<br/>&nbsp;&nbsp;&nbsp;&nbsp;感谢一直以来在致趣的付出以及努力，今天是你的生日，在这个格外重要的日子代表致趣小伙伴们<br/>&nbsp;&nbsp;&nbsp;&nbsp;祝你生日快乐，你最珍贵！</h3>
      <div>
    </div>

    <br/><br/>
    """%(u'郭钰')
    to_emails = ['guoyu@inad.com']
    send_html_mail(u'生日快乐！', recipients=to_emails, body=text)
    

if __name__ == '__main__':
    get_all_today_is_birthday()
