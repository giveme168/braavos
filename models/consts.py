# -*- coding: UTF-8 -*-

#  状态
STATUS_ON = 1         # 有效
STATUS_OFF = 0        # 停用
STATUS_CN = {
    STATUS_OFF: u"暂停",
    STATUS_ON: u"有效"
}

#  客户行业 新增行业只能在列表最后增加
CLIENT_INDUSTRY_LIST = [
    u"IT",
    u"互联网产品",
    u"交友",
    u"化妆品",
    u"品牌公益",
    u"品牌其他",
    u"奢侈品",
    u"家电",
    u"快消",
    u"教育",
    u"数码产品",
    u"旅游",
    u"时尚",
    u"汽车",
    u"活动展会",
    u"电商网站",
    u"移动类",
    u"组织机构",
    u"运动",
    u"酒精类",
    u"金融",
]

CLIENT_INDUSTRY_CN = dict(enumerate(CLIENT_INDUSTRY_LIST))

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
