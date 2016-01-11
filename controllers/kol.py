# -*- coding: UTF-8 -*-
from flask import Blueprint, render_template as tpl

kol_bp = Blueprint('kol', __name__, template_folder='../templates/kol')

KOLS = {'design': [{'name': u'堂邦嘉真街拍哥',
                    'url': 'http://www.douban.com/people/musickenny/',
                    'location': u'广州', 'fans': 44257, 'des': u'街拍达人，相册，博客，摄影',
                    'is_to_work': u'有', 'is_work': u'是', 'score': 6,
                    'contact': u"QQ：178816477<br/>手机：13760720424<br/>广州市白云大道北岭南新世界G20栋103",
                    'other_des': u'佳能S_Gallery拍照；奥迪参与线下同城活动，发布软文日志和广播（图片+文字），LEVIS参与四期传图，参加VANS投票并推荐LookBook，\
                                   三叶草legging设计'},
                   {'name': u'BUTU布兔',
                    'url': 'http://www.douban.com/people/butu/',
                    'location': u'北京', 'fans': 37198, 'des': '插画师、手绘、日记，代表作《地铁》、《教海鸥飞翔的猫》，签约最世文化',
                    'is_to_work': u'有', 'is_work': u'是', 'score': 7,
                    'contact': u"手机：13488828343<br/>QQ：54467051<br/>北京通州区乔庄北街6号院2号楼761",
                    'other_des': u'indigo酒店插画约稿；联想创客线上参与。因为小孩得了抑郁症，所以精力主要放在照顾家庭，表示最近不会再接需要创作的设计类工作。'},
                   {'name': u'過期貓糧',
                    'url': 'http://www.douban.com/people/2848905',
                    'location': u'北京', 'fans': 14800, 'des': '插画师，商务活动获奖用户漫画家，动画师', 'is_to_work': u'有',
                    'is_work': u'是', 'score': 7, 'contact': u"猫粮：18610034714 catfoodcan@foxmail.com；经纪人王先生13701173356<br/>北京市东城区\
                                                              安贞桥环球贸易中心A座1707，SNF SCD王璐",
                    'other_des': u'桑塔纳真情日志、卡萨帝创艺+U红人访谈'},
                   {'name': u'阿科',
                    'url': 'http://www.douban.com/people/cyclediary/',
                    'location': u'上海', 'fans': 11483, 'des': u'上海插画师、绘本创作人、小说作者', 'is_to_work': u'有',
                    'is_work': u'是', 'score': 7, 'contact': u"13916828191，QQ：291155296<br/>徐家汇零陵路天钥新村106号201室",
                    'other_des': u"理想青年；福特翼搏为flash提供插画；金立设计卡通形象；thinkpad s设计约稿；长安汽车手绘；Levi's参与四期传图；Indigo叮叮车设计；\
                                  参与路虎潜匿之光Flash活动；三叶草legging设计"},
                   {'name': u'阿科',
                    'url': 'http://www.douban.com/people/cyclediary/',
                    'location': u'上海', 'fans': 11483, 'des': u'上海插画师、绘本创作人、小说作者', 'is_to_work': u'有',
                    'is_work': u'是', 'score': 7, 'contact': u"13916828191，QQ：291155296<br/>徐家汇零陵路天钥新村106号201室",
                    'other_des': u"理想青年；福特翼搏为flash提供插画；金立设计卡通形象；thinkpad s设计约稿；长安汽车手绘；Levi's参与四期传图；Indigo叮叮车设计；\
                                  参与路虎潜匿之光Flash活动；三叶草legging设计"}],
        'photo': [],
        'topic': [],
        'trip': [],
        'beauty': [],
        'food': [],
        'fashion': [],
        'muisc': [],
        'decoration': [],
        'sport': [],
        'douban': [],
        'tech': [],
        'car': [],
        }


@kol_bp.route('/<type>', methods=['GET'])
def index(type):
    pass
    return tpl('kol/index.html', kols=KOLS[type])
