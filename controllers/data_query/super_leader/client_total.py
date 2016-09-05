# -*- coding: UTF-8 -*-
import datetime
from numpy import array
from flask import Blueprint, request, g, abort, json
from flask import render_template as tpl

from libs.date_helpers import get_monthes_pre_days
from controllers.data_query.helpers.super_leader_helpers import write_client_total_excel

from models.order import Order
from models.associated_douban_order import AssociatedDoubanOrder
from models.douban_order import DoubanOrder

data_query_super_leader_client_total_bp = Blueprint(
    'data_query_super_leader_client_total', __name__, template_folder='../../templates/data_query')


HB_data = [{
    'industry_name': u'IT/家电/运营商',
    'clients': [{
        'name': u'DELL 戴尔', 'client_ids': [336], 'agents': []
    }, {
        'name': u'联想', 'client_ids': [101, 372, 186], 'agents': []
    }, {
        'name': u'ThinkPad', 'client_ids': [594], 'agents':[]
    }, {
        'name': u'三星', 'client_ids': [133, 82], 'agents': []
    }, {
        'name': u'Apple', 'client_ids': [79], 'agents': []
    }, {
        'name': u'高通', 'client_ids': [192], 'agents': []
    }, {
        'name': u'华为', 'client_ids': [102, 200], 'agents':[]
    }, {
        'name': u'惠普 HP', 'client_ids': [56], 'agents':[]
    }, {
        'name': u'Intel', 'client_ids': [51], 'agents':[]
    }, {
        'name': u'亚马逊 - Kindle', 'client_ids': [43], 'agents':[]
    }, {
        'name': u'中国电信', 'client_ids': [138], 'agents':[]
    }, {
        'name': u'联通', 'client_ids': [614], 'agents':[]
    }, {
        'name': u'海尔（海尔集团 - 海尔；海尔集团 - 卡萨帝）', 'client_ids': [327, 21, 1], 'agents':[]
    }, {
        'name': u'微软', 'client_ids': [86, 322], 'agents':[]
    }, {
        'name': u'京东商城（京东、京东-京东金融）', 'client_ids': [103, 640], 'agents':[]
    }, {
        'name': u'VIVO', 'client_ids': [228], 'agents':[]
    }]
}, {
    'industry_name': u'快消',
    'clients': [{
        'name': u'青岛啤酒', 'client_ids': [519], 'agents':[]
    }, {
        'name': u'蒙牛', 'client_ids': [45, 369], 'agents':[]
    }, {
        'name': u'伊利', 'client_ids': [64], 'agents':[]
    }, {
        'name': u'红牛', 'client_ids': [105], 'agents':[]
    }, {
        'name': u'Mars', 'client_ids': [], 'agents':[]
    }]
}, {
    'industry_name': u'汽车',
    'clients': [{
        'name': u'进口大众', 'client_ids': [174], 'agents':[]
    }, {
        'name': u'一汽大众', 'client_ids': [5, 399, 385, 117], 'agents':[]
    }, {
        'name': u'东风标致', 'client_ids': [35], 'agents':[]
    }, {
        'name': u'宝马', 'client_ids': [4], 'agents':[]
    }, {
        'name': u'MINI', 'client_ids': [320], 'agents':[]
    }, {
        'name': u'奔驰', 'client_ids': [164], 'agents':[]
    }, {
        'name': u'英菲尼迪', 'client_ids': [], 'agents':[]
    }, {
        'name': u'雷克萨斯 Lexus', 'client_ids': [90], 'agents':[]
    }, {
        'name': u'奥迪', 'client_ids': [118], 'agents':[]
    }, {
        'name': u'长安马自达', 'client_ids': [130], 'agents':[]
    }, {
        'name': u'东风悦达起亚 KIA', 'client_ids': [290], 'agents':[]
    }, {
        'name': u'东风本田', 'client_ids': [448], 'agents':[]
    }, {
        'name': u'东风雪铁龙', 'client_ids': [166], 'agents':[]
    }, {
        'name': u'奔驰 - Smart', 'client_ids': [164], 'agents':[]
    }, {
        'name': u'北京现代', 'client_ids': [109], 'agents':[]
    }, {
        'name': u'北京汽车', 'client_ids': [42], 'agents':[]
    }, {
        'name': u'丰田', 'client_ids': [46, 91, 242], 'agents':[]
    }, {
        'name': u'雷诺', 'client_ids': [75], 'agents':[]
    }, {
        'name': u'讴歌', 'client_ids': [95], 'agents':[]
    }, {
        'name': u'一汽马自达', 'client_ids': [], 'agents':[]
    }, {
        'name': u'马自达中国', 'client_ids': [83], 'agents':[]
    }, {
        'name': u'大众中国', 'client_ids': [119], 'agents':[]
    }]
}, {
    'industry_name': u'其他',
    'clients': [{
        'name': u'仟金所', 'client_ids': [501], 'agents':[]
    }, {
        'name': u'中国银行', 'client_ids': [253], 'agents':[]
    }, {
        'name': u'英国航空', 'client_ids': [104], 'agents':[]
    }]
}]


HD_data = [{
    'industry_name': u'汽车',
    'clients': [{
        'name': u'东风雪铁龙', 'client_ids': [166], 'agents':[]
    }, {
        'name': u'捷豹', 'client_ids': [554], 'agents':[]
    }, {
        'name': u'通用 - 别克', 'client_ids': [9], 'agents':[]
    }, {
        'name': u'VOLVO', 'client_ids': [628], 'agents':[]
    }, {
        'name': u'斯柯达', 'client_ids': [66], 'agents':[]
    }, {
        'name': u'上海大众', 'client_ids': [111], 'agents':[]
    }, {
        'name': u'凯迪拉克', 'client_ids': [123], 'agents':[]
    }, {
        'name': u'长安马自达', 'client_ids': [130], 'agents':[]
    }, {
        'name': u'MG', 'client_ids': [33], 'agents':[]
    }, {
        'name': u'路虎', 'client_ids': [116], 'agents':[]
    }, {
        'name': u'纳智捷', 'client_ids': [99], 'agents':[]
    }, {
        'name': u'福特', 'client_ids': [112, 307, 391], 'agents':[]
    }, {
        'name': u'雪佛兰（含科帕奇、科鲁兹）', 'client_ids': [260, 387, 240], 'agents':[]
    }, {
        'name': u'江淮汽车', 'client_ids': [634], 'agents':[]
    }, {
        'name': u'林肯', 'client_ids': [149], 'agents':[]
    }, {
        'name': u'路虎', 'client_ids': [116], 'agents':[]
    }]
}, {
    'industry_name': u'化妆品&奢侈品',
    'clients': [{
        'name': u'娇韵诗', 'client_ids': [638], 'agents':[]
    }, {
        'name': u'Sisley', 'client_ids': [629], 'agents':[]
    }, {
        'name': u'Fresh', 'client_ids': [156], 'agents':[]
    }, {
        'name': u'雅诗兰黛（雅诗兰黛集团 - 雅诗兰黛红石榴、雅诗兰黛集团 - 倩碧）', 'client_ids': [146, 171], 'agents':[]
    }, {
        'name': u'La Mer 海蓝之谜', 'client_ids': [], 'agents':[]
    }, {
        'name': u'珀莱雅', 'client_ids': [137], 'agents':[]
    }, {
        'name': u'自然堂', 'client_ids': [107], 'agents':[]
    }, {
        'name': u'资生堂（资生堂 - ZA睫毛膏、资生堂 - 泊美）', 'client_ids': [500, 561], 'agents':[]
    }, {
        'name': u'妮维雅', 'client_ids': [163], 'agents':[]
    }, {
        'name': u'茱莉蔻', 'client_ids': [143], 'agents':[]
    }, {
        'name': u'Innisfree', 'client_ids': [128], 'agents':[]
    }, {
        'name': u'欧莱雅集团 - 兰蔻', 'client_ids': [6], 'agents':[]
    }, {
        'name': u'碧欧泉 Biotherm', 'client_ids': [167], 'agents':[]
    }, {
        'name': u"科颜氏（契尔氏 or Kiehl's）", 'client_ids': [], 'agents':[]
    }, {
        'name': u'理肤泉', 'client_ids': [60, 419], 'agents':[]
    }, {
        'name': u'羽西', 'client_ids': [63], 'agents':[]
    }, {
        'name': u'欧莱雅中国', 'client_ids': [89], 'agents':[]
    }, {
        'name': u'植村秀', 'client_ids': [19], 'agents':[]
    }, {
        'name': u'欧莱雅集团 - 美宝莲', 'client_ids': [7], 'agents':[]
    }, {
        'name': u'家化高夫', 'client_ids': [73], 'agents':[]
    }, {
        'name': u'欧莱雅集团 - YSL 圣罗兰', 'client_ids': [29], 'agents':[]
    }, {
        'name': u'Giorgio Armani', 'client_ids': [26], 'agents':[]
    }, {
        'name': u'Clarisonic', 'client_ids': [25, 494], 'agents':[]
    }, {
        'name': u'Cartier', 'client_ids': [456], 'agents':[]
    }, {
        'name': u'Tiffany', 'client_ids': [292], 'agents':[]
    }, {
        'name': u'积家 JLC', 'client_ids': [125], 'agents':[]
    }, {
        'name': u'派克', 'client_ids': [294], 'agents':[]
    }, {
        'name': u'Armani', 'client_ids': [208], 'agents':[]
    }, {
        'name': u'Burberry', 'client_ids': [142], 'agents':[]
    }, {
        'name': u'CHANEL', 'client_ids': [8], 'agents':[]
    }, {
        'name': u'Dior', 'client_ids': [16], 'agents':[]
    }, {
        'name': u'万宝龙', 'client_ids': [479], 'agents':[]
    }, {
        'name': u'Vans', 'client_ids': [201], 'agents':[]
    }, {
        'name': u'索尼 Sony', 'client_ids': [354], 'agents':[]
    }]
}, {
    'industry_name': u'IT&家电',
    'clients': [{
        'name': 'APPLE', 'client_ids': [79], 'agents':[]
    }, {
        'name': u'西门子', 'client_ids': [36], 'agents':[]
    }, {
        'name': u'乐视', 'client_ids': [526, 140], 'agents':[]
    }, {
        'name': u'微软', 'client_ids': [86, 322], 'agents':[]
    }, {
        'name': u'飞利浦 PHILIPS', 'client_ids': [74, 367, 333], 'agents':[]
    }, {
        'name': u'博世 BOSCH', 'client_ids': [212], 'agents':[]
    }, {
        'name': u'长虹', 'client_ids': [148], 'agents':[]
    }, {
        'name': u'老板电器', 'client_ids': [57], 'agents':[]
    }, {
        'name': u'卡西欧', 'client_ids': [221], 'agents':[]
    }, {
        'name': 'Fossil', 'client_ids': [98], 'agents':[]
    }, {
        'name': u'方太', 'client_ids': [621], 'agents':[]
    }, {
        'name': u'Dyson 戴森', 'client_ids': [188], 'agents':[]
    }]
}, {
    'industry_name': u'快消&运动',
    'clients': [{
        'name': 'The North Face', 'client_ids': [28], 'agents':[]
    }, {
        'name': 'LEE', 'client_ids': [27], 'agents':[]
    }, {
        'name': 'C&A', 'client_ids': [256], 'agents':[]
    }, {
        'name': 'H&M', 'client_ids': [152], 'agents':[]
    }, {
        'name': 'Abercrombie & Fitch', 'client_ids': [18], 'agents':[]
    }, {
        'name': 'Nike', 'client_ids': [15, 232], 'agents':[]
    }, {
        'name': u'高洁丝', 'client_ids': [298], 'agents':[]
    }, {
        'name': u'康师傅', 'client_ids': [280], 'agents':[]
    }, {
        'name': 'Zespri', 'client_ids': [344], 'agents':[]
    }, {
        'name': u'桂格', 'client_ids': [276], 'agents':[]
    }, {
        'name': 'O.B.', 'client_ids': [68], 'agents':[]
    }, {
        'name': u'星巴克', 'client_ids': [129], 'agents':[]
    }, {
        'name': u'奥利奥', 'client_ids': [41], 'agents':[]
    }, {
        'name': u'统一', 'client_ids': [94], 'agents':[]
    }, {
        'name': u'Tiger 虎牌啤酒', 'client_ids': [144], 'agents':[]
    }, {
        'name': u'舒蕾', 'client_ids': [598], 'agents':[]
    }, {
        'name': u'李锦记', 'client_ids': [85], 'agents':[]
    }, {
        'name': 'Levis', 'client_ids': [483], 'agents':[]
    }, {
        'name': 'Adidas', 'client_ids': [54], 'agents':[]
    }, {
        'name': u'马爹利', 'client_ids': [150], 'agents':[]
    }, {
        'name': u'蘑菇街', 'client_ids': [297], 'agents':[]
    }]
}, {
    'industry_name': u'金融&其他',
    'clients': [{
        'name': u'太平洋保险', 'client_ids': [131], 'agents':[]
    }, {
        'name': u'汇添富', 'client_ids': [289], 'agents':[]
    }, {
        'name': u'陆金所', 'client_ids': [22], 'agents':[]
    }, {
        'name': u'平安科技', 'client_ids': [], 'agents':[]
    }, {
        'name': u'易方达', 'client_ids': [347], 'agents':[]
    }, {
        'name': u'恒大金服', 'client_ids': [592], 'agents':[]
    }, {
        'name': u'浦发银行', 'client_ids': [531], 'agents':[]
    }, {
        'name': u'玖富', 'client_ids': [543], 'agents':[]
    }, {
        'name': u'Visa', 'client_ids': [237], 'agents':[]
    }, {
        'name': u'壳牌', 'client_ids': [141], 'agents':[]
    }, {
        'name': u'俊启', 'client_ids': [631], 'agents':[]
    }, {
        'name': u'巴斯夫', 'client_ids': [52, 264], 'agents':[]
    }, {
        'name': u'一号店', 'client_ids': [121], 'agents':[]
    }, {
        'name': u'小红书', 'client_ids': [293], 'agents':[]
    }, {
        'name': u'苏宁', 'client_ids': [268], 'agents':[]
    }, {
        'name': u'上海移动', 'client_ids': [191], 'agents':[]
    }, {
        'name': u'汉莎航空', 'client_ids': [249], 'agents':[]
    }, {
        'name': u'芬兰航空', 'client_ids': [335], 'agents':[]
    }, {
        'name': u'银联国际', 'client_ids': [165], 'agents':[]
    }]
}]


HN_data = [{
    'industry_name': u'IT/互联网',
    'clients': [{
        'name': u'华为荣耀', 'client_ids': [200], 'agents':[]
    }, {
        'name': u'腾讯游戏', 'client_ids': [47, 566], 'agents':[]
    }, {
        'name': u'网易', 'client_ids': [65, 132], 'agents':[]
    }, {
        'name': u'康佳', 'client_ids': [504], 'agents':[]
    }, {
        'name': u'创维', 'client_ids': [214], 'agents':[]
    }, {
        'name': u'小熊电器', 'client_ids': [58], 'agents':[]
    }, {
        'name': u'美的', 'client_ids': [135, 206, 234, 235], 'agents':[]
    }, {
        'name': u'OPPO', 'client_ids': [169], 'agents':[]
    }, {
        'name': u'VIVO', 'client_ids': [228], 'agents':[]
    }, {
        'name': u'金立', 'client_ids': [366], 'agents':[]
    }, {
        'name': u'魅族', 'client_ids': [528], 'agents':[]
    }, {
        'name': u'卡尔蔡司Zeiss', 'client_ids': [93], 'agents':[]
    }, {
        'name': u'nubia', 'client_ids': [49], 'agents':[]
    }, {
        'name': u'oneplus', 'client_ids': [72], 'agents':[]
    }]
}, {
    'industry_name': u'快消',
    'clients': [{
        'name': u'曜能量', 'client_ids': [77], 'agents':[]
    }, {
        'name': u'乐堡啤酒', 'client_ids': [69], 'agents':[]
    }, {
        'name': u'博朗', 'client_ids': [195], 'agents':[]
    }, {
        'name': u'益达', 'client_ids': [170], 'agents':[]
    }, {
        'name': u'美赞臣', 'client_ids': [106], 'agents':[]
    }, {
        'name': u'统一', 'client_ids': [94], 'agents':[]
    }, {
        'name': u'宝洁 - 碧浪', 'client_ids': [44], 'agents':[]
    }, {
        'name': u'护舒宝', 'client_ids': [40], 'agents':[]
    }, {
        'name': u'宝洁 - 沙宣', 'client_ids': [3], 'agents':[]
    }, {
        'name': u'新希望', 'client_ids': [352], 'agents':[]
    }, {
        'name': u'舒肤佳', 'client_ids': [278], 'agents':[]
    }, {
        'name': u'曼秀雷敦', 'client_ids': [346], 'agents':[]
    }, {
        'name': u'伊卡璐', 'client_ids': [403], 'agents':[]
    }, {
        'name': u'达能（脉动）', 'client_ids': [426], 'agents':[]
    }, {
        'name': u'宝洁 - 玉兰油 Olay', 'client_ids': [254], 'agents':[]
    }, {
        'name': u'美即', 'client_ids': [457], 'agents':[]
    }, {
        'name': u'SK-II', 'client_ids': [24], 'agents':[]
    }, {
        'name': u'屈臣氏（屈臣氏 - 苏打水、屈臣氏 - 蒸馏水）', 'client_ids': [175, 274], 'agents':[]
    }]
}, {
    'industry_name': u'时尚',
    'clients': [{
        'name': 'Abercrombie & Fitch', 'client_ids': [18], 'agents':[]
    }, {
        'name': '361度', 'client_ids': [464], 'agents':[]
    }, {
        'name': '周生生', 'client_ids': [76], 'agents':[]
    }]
}, {
    'industry_name': u'汽车',
    'clients': [{
        'name': '江淮汽车', 'client_ids': [634], 'agents':[]
    }, {
        'name': '东风日产', 'client_ids': [48], 'agents':[]
    }, {
        'name': '广汽丰田/传祺', 'client_ids': [416], 'agents':[]
    }, {
        'name': '纳智捷', 'client_ids': [99], 'agents':[]
    }, {
        'name': '海马汽车', 'client_ids': [81], 'agents':[]
    }, {
        'name': '长安汽车', 'client_ids': [605, 563, 400, 324], 'agents':[]
    }, {
        'name': '比亚迪', 'client_ids': [271], 'agents':[]
    }, {
        'name': '菲亚特', 'client_ids': [97], 'agents':[]
    }]
}, {
    'industry_name': u'金融/旅游/其他',
    'clients': [{
        'name': '亚航/亚洲航空', 'client_ids': [11], 'agents':[]
    }, {
        'name': '澳门威尼斯人酒店', 'client_ids': [157], 'agents':[]
    }, {
        'name': '四川移动', 'client_ids': [151, 453], 'agents':[]
    }, {
        'name': '平安集团', 'client_ids': [23, 350, 315, 535, 556], 'agents':[]
    }, {
        'name': '中国移动', 'client_ids': [493, 151, 604], 'agents':[]
    }, {
        'name': '广东电信', 'client_ids': [379], 'agents':[]
    }, {
        'name': '中信银行', 'client_ids': [475], 'agents':[]
    }, {
        'name': '平安车险', 'client_ids': [315], 'agents':[]
    }, {
        'name': '平安银行', 'client_ids': [23], 'agents':[]
    }]
}]


def pre_month_money(money, start, end, locations):
    if money:
        pre_money = float(money) / ((end - start).days + 1)
    else:
        pre_money = 0
    pre_month_days = get_monthes_pre_days(start, end)
    pre_month_money_data = []
    for k in pre_month_days:
        money = pre_money * k['days'] / len(set(locations))
        pre_month_money_data.append({'month': k['month'], 'money': money})
    return pre_month_money_data


def _format_client_order(order, year, ass_douban_order_ids):
    dict_order = {}
    try:
        client_order = order.client_order
        dict_order['client_start'] = client_order.client_start
        dict_order['client_end'] = client_order.client_start
        dict_order['agent_id'] = client_order.agent.id
        dict_order['agent_name'] = client_order.agent.name
        dict_order['client_id'] = client_order.client.id
        dict_order['contract_status'] = client_order.contract_status
        dict_order['status'] = client_order.status
        dict_order['locations'] = client_order.locations
        dict_order['contract'] = client_order.contract
        if order.id in ass_douban_order_ids:
            is_c_douban = True
        else:
            is_c_douban = False
        '''
        direct_sales = client_order.direct_sales
        agent_sales = client_order.agent_sales
        sales = direct_sales + agent_sales
        if 148 in [int(k.id) for k in sales]:
            is_media_order = True
        else:
            is_media_order = False
        '''
        # 计算两年前的开始结束时间
        b_y_start = datetime.datetime.strptime(str(year - 2), '%Y').date()
        b_y_end = datetime.datetime.strptime(str(year - 2) + '-12-01', '%Y-%m-%d').date()
        # 计算上一年的开始时间
        l_start = datetime.datetime.strptime(str(year - 1), '%Y').date()
        l_end = datetime.datetime.strptime(str(year - 1) + '-12-01', '%Y-%m-%d').date()
        # 计算当年每季度的开始结束时间
        Q1_monthes = [datetime.datetime.strptime(str(year) + "-" + str(k), "%Y-%m").date()
                      for k in range(1, 4)]
        Q2_monthes = [datetime.datetime.strptime(str(year) + "-" + str(k), "%Y-%m").date()
                      for k in range(4, 7)]
        Q3_monthes = [datetime.datetime.strptime(str(year) + "-" + str(k), "%Y-%m").date()
                      for k in range(7, 10)]
        Q4_monthes = [datetime.datetime.strptime(str(year) + "-" + str(k), "%Y-%m").date()
                      for k in range(10, 13)]

        if is_c_douban:
            pre_month_money_data = pre_month_money(order.medium_money,
                                                   dict_order['client_start'],
                                                   dict_order['client_end'],
                                                   dict_order['locations'])
            b_y_douban_money = float(sum([k['money'] for k in pre_month_money_data
                                          if k['month'] >= b_y_start and k['month'] <= b_y_end]))
            l_douban_money = float(sum([k['money'] for k in pre_month_money_data
                                        if k['month'] >= l_start and k['month'] <= l_end]))
            Q1_douban_money = float(sum([k['money'] for k in pre_month_money_data
                                         if k['month'] >= Q1_monthes[0] and k['month'] <= Q1_monthes[-1]]))
            Q2_douban_money = float(sum([k['money'] for k in pre_month_money_data
                                         if k['month'] >= Q2_monthes[0] and k['month'] <= Q2_monthes[-1]]))
            Q3_douban_money = float(sum([k['money'] for k in pre_month_money_data
                                         if k['month'] >= Q3_monthes[0] and k['month'] <= Q3_monthes[-1]]))
            Q4_douban_money = float(sum([k['money'] for k in pre_month_money_data
                                         if k['month'] >= Q4_monthes[0] and k['month'] <= Q4_monthes[-1]]))
            b_y_client_money = 0.0
            l_client_money = 0.0
            Q1_client_money = 0.0
            Q2_client_money = 0.0
            Q3_client_money = 0.0
            Q4_client_money = 0.0
            '''
            Q1_media_money = 0
            Q2_media_money = 0
            Q3_media_money = 0
            Q4_media_money = 0
            '''
        else:
            b_y_douban_money = 0.0
            l_douban_money = 0.0
            Q1_douban_money = 0.0
            Q2_douban_money = 0.0
            Q3_douban_money = 0.0
            Q4_douban_money = 0.0
            pre_month_money_data = pre_month_money(order.sale_money,
                                                   dict_order['client_start'],
                                                   dict_order['client_end'],
                                                   dict_order['locations'])
            b_y_client_money = float(sum([k['money'] for k in pre_month_money_data
                                          if k['month'] >= b_y_start and k['month'] <= b_y_end]))
            l_client_money = float(sum([k['money'] for k in pre_month_money_data
                                        if k['month'] >= l_start and k['month'] <= l_end]))
            '''
            if is_media_order:
                Q1_media_money = sum([k['money'] for k in pre_month_money_data
                                      if k['month'] >= Q1_monthes[0] and k['month'] <= Q1_monthes[-1]])
                Q2_media_money = sum([k['money'] for k in pre_month_money_data
                                      if k['month'] >= Q2_monthes[0] and k['month'] <= Q2_monthes[-1]])
                Q3_media_money = sum([k['money'] for k in pre_month_money_data
                                      if k['month'] >= Q3_monthes[0] and k['month'] <= Q3_monthes[-1]])
                Q4_media_money = sum([k['money'] for k in pre_month_money_data
                                      if k['month'] >= Q4_monthes[0] and k['month'] <= Q4_monthes[-1]])
                Q1_client_money = 0
                Q2_client_money = 0
                Q3_client_money = 0
                Q4_client_money = 0
            else:
                Q1_client_money = sum([k['money'] for k in pre_month_money_data
                                       if k['month'] >= Q1_monthes[0] and k['month'] <= Q1_monthes[-1]])
                Q2_client_money = sum([k['money'] for k in pre_month_money_data
                                       if k['month'] >= Q2_monthes[0] and k['month'] <= Q2_monthes[-1]])
                Q3_client_money = sum([k['money'] for k in pre_month_money_data
                                       if k['month'] >= Q3_monthes[0] and k['month'] <= Q3_monthes[-1]])
                Q4_client_money = sum([k['money'] for k in pre_month_money_data
                                       if k['month'] >= Q4_monthes[0] and k['month'] <= Q4_monthes[-1]])
                Q1_media_money = 0
                Q2_media_money = 0
                Q3_media_money = 0
                Q4_media_money = 0
            '''
            Q1_client_money = float(sum([k['money'] for k in pre_month_money_data
                                         if k['month'] >= Q1_monthes[0] and k['month'] <= Q1_monthes[-1]]))
            Q2_client_money = float(sum([k['money'] for k in pre_month_money_data
                                         if k['month'] >= Q2_monthes[0] and k['month'] <= Q2_monthes[-1]]))
            Q3_client_money = float(sum([k['money'] for k in pre_month_money_data
                                         if k['month'] >= Q3_monthes[0] and k['month'] <= Q3_monthes[-1]]))
            Q4_client_money = float(sum([k['money'] for k in pre_month_money_data
                                         if k['month'] >= Q4_monthes[0] and k['month'] <= Q4_monthes[-1]]))
        # money列表一共12项，对应页面上的12个金额，根据每项金额的值拼接的
        now_year_money = Q1_client_money + Q1_douban_money + Q2_client_money + Q2_douban_money + \
            Q3_client_money + Q3_douban_money + Q4_client_money + Q4_douban_money
        dict_order['money'] = [b_y_client_money, b_y_douban_money, b_y_client_money + b_y_douban_money,
                               l_client_money, l_douban_money, l_client_money + l_douban_money,
                               0.0,
                               Q1_client_money, Q1_douban_money,
                               Q2_client_money, Q2_douban_money,
                               Q3_client_money, Q3_douban_money,
                               Q4_client_money, Q4_douban_money,
                               float(now_year_money), 0.0]
    except:
        dict_order['status'] = 0
        dict_order['contract_status'] = 0
        dict_order['contract'] = ''
    return dict_order


def _format_douban_order(order, year):
    dict_order = {}
    dict_order['client_start'] = order.client_start
    dict_order['client_end'] = order.client_start
    dict_order['agent_id'] = order.agent.id
    dict_order['agent_name'] = order.agent.name
    dict_order['client_id'] = order.client.id
    dict_order['contract_status'] = order.contract_status
    dict_order['status'] = order.status
    dict_order['locations'] = order.locations
    dict_order['contract'] = order.contract
    pre_month_money_data = pre_month_money(order.money,
                                           dict_order['client_start'],
                                           dict_order['client_end'],
                                           dict_order['locations'])

    # 计算两年前的开始结束时间
    b_y_start = datetime.datetime.strptime(str(year - 2), '%Y').date()
    b_y_end = datetime.datetime.strptime(str(year - 2) + '-12-01', '%Y-%m-%d').date()
    # 计算上一年的开始时间
    l_start = datetime.datetime.strptime(str(year - 1), '%Y').date()
    l_end = datetime.datetime.strptime(str(year - 1) + '-12-01', '%Y-%m-%d').date()
    # 计算当年每季度的开始结束时间
    Q1_monthes = [datetime.datetime.strptime(str(year) + "-" + str(k), "%Y-%m").date()
                  for k in range(1, 4)]
    Q2_monthes = [datetime.datetime.strptime(str(year) + "-" + str(k), "%Y-%m").date()
                  for k in range(4, 7)]
    Q3_monthes = [datetime.datetime.strptime(str(year) + "-" + str(k), "%Y-%m").date()
                  for k in range(7, 10)]
    Q4_monthes = [datetime.datetime.strptime(str(year) + "-" + str(k), "%Y-%m").date()
                  for k in range(10, 13)]

    # money列表一共12项，对应页面上的12个金额，根据每项金额的值拼接的
    b_y_money = float(sum([k['money'] for k in pre_month_money_data if k[
                      'month'] >= b_y_start and k['month'] <= b_y_end]))
    l_money = float(sum([k['money'] for k in pre_month_money_data if k['month'] >= l_start and k['month'] <= l_end]))
    Q1_money = float(sum([k['money'] for k in pre_month_money_data
                          if k['month'] >= Q1_monthes[0] and k['month'] <= Q1_monthes[-1]]))
    Q2_money = float(sum([k['money'] for k in pre_month_money_data
                          if k['month'] >= Q2_monthes[0] and k['month'] <= Q2_monthes[-1]]))
    Q3_money = float(sum([k['money'] for k in pre_month_money_data
                          if k['month'] >= Q3_monthes[0] and k['month'] <= Q3_monthes[-1]]))
    Q4_money = float(sum([k['money'] for k in pre_month_money_data
                          if k['month'] >= Q4_monthes[0] and k['month'] <= Q4_monthes[-1]]))
    dict_order['money'] = [0.0, b_y_money, b_y_money,
                           0.0, l_money, l_money,
                           0.0,
                           0.0, Q1_money,
                           0.0, Q2_money,
                           0.0, Q3_money,
                           0.0, Q4_money,
                           Q1_money + Q2_money + Q3_money + Q4_money,
                           0.0]
    return dict_order


def _fix_client_data(data, orders, location):
    t_money = array([float(0) for k in range(17)])
    for k in data:
        k['th_n'] = 0
        for c in k['clients']:
            agents_obj = {}
            for o in orders:
                if o['client_id'] in c['client_ids'] and location in o['locations']:
                    if o['agent_name'] in agents_obj:
                        agents_obj[o['agent_name']] += array(o['money'])
                    else:
                        agents_obj[o['agent_name']] = array(o['money'])
                    # 计算客户增长率
                    if agents_obj[o['agent_name']][2]:
                        agents_obj[o['agent_name']][6] = (agents_obj[o['agent_name']][5] -
                                                          agents_obj[o['agent_name']][2]) / \
                            agents_obj[o['agent_name']][2] * 100
                    else:
                        agents_obj[o['agent_name']][6] = 0
                    if agents_obj[o['agent_name']][5]:
                        agents_obj[o['agent_name']][16] = (agents_obj[o['agent_name']][15] -
                                                           agents_obj[o['agent_name']][5]) / \
                            agents_obj[o['agent_name']][5] * 100
                    else:
                        agents_obj[o['agent_name']][16] = 0
                    t_money += array(o['money'])
            # 客户下代理信息详情
            c['agents'] = agents_obj
            c['agent_count'] = len(c['agents']) or 1
            k['th_n'] += len(c['agents']) or 1

            # 合并客户下的代理信息用于画图
            c['client_money'] = array([float(0) for i in range(17)])
            for c_k, c_v in agents_obj.iteritems():
                c['client_money'] += array(c_v)
    # 计算区域客户增值率
    if t_money[2]:
        t_money[6] = (t_money[5] - t_money[2]) / float(t_money[2]) * 100
    else:
        t_money[6] = 0
    if t_money[5]:
        t_money[16] = (t_money[15] - t_money[5]) / float(t_money[5]) * 100
    else:
        t_money[16] = 0
    return t_money, data


@data_query_super_leader_client_total_bp.route('/client_order', methods=['GET'])
def index():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance()):
        abort(403)
    location = int(request.values.get('location', 1))
    now_date = datetime.datetime.now()
    year = int(request.values.get('year', now_date.year))
    # 获取所有关联豆瓣订单，用于判断媒体订单是否是关联豆瓣订单，全部取出减少链接数据库时间
    ass_douban_order_ids = [k.medium_order_id for k in AssociatedDoubanOrder.all()]
    orders = [_format_douban_order(k, year) for k in DoubanOrder.all()
              if k.client_start.year >= year - 2 and k.client_start.year <= year]
    orders += [_format_client_order(k, year, ass_douban_order_ids) for k in Order.all()
               if k.medium_start.year >= year - 2 and k.medium_start.year <= year]
    # 去掉撤单、申请中的合同
    orders = [k for k in orders if k['contract_status'] in [2, 4, 5, 10, 19, 20] and k['status'] == 1]
    if location == 1:
        money, data = _fix_client_data(HB_data, orders, location)
    elif location == 2:
        money, data = _fix_client_data(HD_data, orders, location)
    elif location == 3:
        money, data = _fix_client_data(HN_data, orders, location)
    action = request.values.get('action', '')
    if action == 'excel':
        return write_client_total_excel(year=year, data=data, money=money, location=location)
    # 组装数据用于画图
    categories_1 = []
    series_1 = [{
        'name': str(year - 2) + u'年新媒体',
        'data': [],
        'stack': str(year - 2)
    }, {
        'name': str(year - 2) + u'年豆瓣',
        'data': [],
        'stack': str(year - 2)
    }, {
        'name': str(year - 1) + u'年新媒体',
        'data': [],
        'stack': str(year - 1)
    }, {
        'name': str(year - 1) + u'年豆瓣',
        'data': [],
        'stack': str(year - 1)
    }, {
        'name': str(year) + u'年新媒体',
        'data': [],
        'stack': str(year)
    }, {
        'name': str(year) + u'年豆瓣',
        'data': [],
        'stack': str(year)
    }]
    categories_2 = []
    series_2 = [{
        'name': str(year - 2) + u'年新媒体',
        'data': [],
        'stack': str(year - 2)
    }, {
        'name': str(year - 2) + u'年豆瓣',
        'data': [],
        'stack': str(year - 2)
    }, {
        'name': str(year - 1) + u'年新媒体',
        'data': [],
        'stack': str(year - 1)
    }, {
        'name': str(year - 1) + u'年豆瓣',
        'data': [],
        'stack': str(year - 1)
    }, {
        'name': str(year) + u'年新媒体',
        'data': [],
        'stack': str(year)
    }, {
        'name': str(year) + u'年豆瓣',
        'data': [],
        'stack': str(year)
    }]
    for k in data:
        clients = k['clients']
        for c in range(len(clients)):
            if c <= len(clients) / 2:
                categories_1.append(clients[c]['name'])
                series_1[0]['data'].append(clients[c]['client_money'][0])
                series_1[1]['data'].append(clients[c]['client_money'][1])
                series_1[2]['data'].append(clients[c]['client_money'][3])
                series_1[3]['data'].append(clients[c]['client_money'][4])
                series_1[4]['data'].append(clients[c]['client_money'][7] + clients[c]['client_money'][9] +
                                           clients[c]['client_money'][11] + clients[c]['client_money'][13])
                series_1[5]['data'].append(clients[c]['client_money'][8] + clients[c]['client_money'][10] +
                                           clients[c]['client_money'][12] + clients[c]['client_money'][14])
            else:
                categories_2.append(clients[c]['name'])
                series_2[0]['data'].append(clients[c]['client_money'][0])
                series_2[1]['data'].append(clients[c]['client_money'][1])
                series_2[2]['data'].append(clients[c]['client_money'][3])
                series_2[3]['data'].append(clients[c]['client_money'][4])
                series_2[4]['data'].append(clients[c]['client_money'][7] + clients[c]['client_money'][9] +
                                           clients[c]['client_money'][11] + clients[c]['client_money'][13])
                series_2[5]['data'].append(clients[c]['client_money'][8] + clients[c]['client_money'][10] +
                                           clients[c]['client_money'][12] + clients[c]['client_money'][14])
    return tpl('/data_query/super_leader/client_total.html', year=year,
               data=data, money=money, location=location, categories_1=json.dumps(categories_1),
               series_1=json.dumps(series_1), categories_2=json.dumps(categories_2), series_2=json.dumps(series_2))
