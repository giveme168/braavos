# encoding: utf-8
import os
import sys
#sys.path.insert(0, os.path.abspath('.'))
sys.path.append('/home/inad/apps/braavos/releases/current') 
from app import app
from models.user import User
from libs.mail import send_html_mail




def get_all_today_is_birthday():
    text = u"""
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="renderer" content="webkit">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>生日快乐</title>
    <link rel="stylesheet" href="http://cdn.bootcss.com/bootstrap/3.3.5/css/bootstrap.min.css">
  </head>
  <body>
    <div class="container-fluid" tabindex="-1" style="background-image:url(http://z.inad.com/static/imgs/brithday.jpg);background-repeat: no-repeat; background-position: center 0;
    min-height:660px;
    position: relative;">
      <h3 style="position:absolute;
left:40%;top:20%;color:#FF44AA; font-family:Microsoft YaHei;width:350px;">亲爱的 %s：<br/>
&nbsp;&nbsp;&nbsp;&nbsp;感谢一直以来在致趣的付出以<br/>
及努力，今天是你的生日，在这<br/>
个格外重要的日子代表致趣小伙<br/>伴们<br/>
&nbsp;&nbsp;&nbsp;&nbsp;祝你生日快乐，你最珍贵！
    </h3>
    </div>
    

  </body>
</html>
    """%(u'郭钰')
    to_emails = ['guoyu@inad.com']
    send_html_mail(u'生日快乐！', recipients=to_emails, body=text)
    

if __name__ == '__main__':
    get_all_today_is_birthday()
