# -*- coding: UTF-8 -*-
import datetime
import calendar as cal
from flask import url_for, g

from . import db, BaseModelMixin
from .user import User, TEAM_LOCATION_CN
from models.mixin.comment import CommentMixin
from models.mixin.attachment import AttachmentMixin
from models.attachment import ATTACHMENT_STATUS_PASSED, ATTACHMENT_STATUS_REJECT
from consts import DATE_FORMAT
from libs.mail import mail
from libs.date_helpers import get_monthes_pre_days


CONTRACT_TYPE_NORMAL = 0
CONTRACT_TYPE_SPECIAL = 1
CONTRACT_TYPE_CN = {
    CONTRACT_TYPE_NORMAL: u"标准",
    CONTRACT_TYPE_SPECIAL: u"非标"
}

SALE_TYPE_AGENT = 0
SALE_TYPE_DIRECT = 1
SALE_TYPE_CN = {
    SALE_TYPE_AGENT: u"代理",
    SALE_TYPE_DIRECT: u"直客",
}

RESOURCE_TYPE_AD = 0
RESOURCE_TYPE_CAMPAIGN = 1
RESOURCE_TYPE_FRAME = 2
RESOURCE_TYPE_OTHER = 4
RESOURCE_TYPE_CN = {
    RESOURCE_TYPE_AD: u"硬广",
    RESOURCE_TYPE_CAMPAIGN: u"互动",
    # RESOURCE_TYPE_FRAME: u"框架",
    RESOURCE_TYPE_OTHER: u"其他"
}

CONTRACT_STATUS_NEW = 0
CONTRACT_STATUS_APPLYCONTRACT = 1
CONTRACT_STATUS_APPLYPASS = 2
CONTRACT_STATUS_APPLYREJECT = 3
CONTRACT_STATUS_APPLYPRINT = 4
CONTRACT_STATUS_PRINTED = 5
CONTRACT_STATUS_DELETEAPPLY = 7
CONTRACT_STATUS_DELETEAGREE = 8
CONTRACT_STATUS_DELETEPASS = 9
CONTRACT_STATUS_FINISH = 20
CONTRACT_STATUS_CN = {
    CONTRACT_STATUS_NEW: u"新建",
    CONTRACT_STATUS_APPLYCONTRACT: u"申请合同号中...",
    CONTRACT_STATUS_APPLYPASS: u"申请合同号通过",
    CONTRACT_STATUS_APPLYREJECT: u"申请合同号未通过",
    CONTRACT_STATUS_APPLYPRINT: u"申请打印中...",
    CONTRACT_STATUS_PRINTED: u"打印完毕",
    CONTRACT_STATUS_DELETEAPPLY: u'撤单申请中...',
    CONTRACT_STATUS_DELETEAGREE: u'确认撤单',
    CONTRACT_STATUS_DELETEPASS: u'同意撤单',
    CONTRACT_STATUS_FINISH: u'项目归档'
}

STATUS_DEL = 0
STATUS_ON = 1
STATUS_CN = {
    STATUS_DEL: u'删除',
    STATUS_ON: u'正常',
}

BACK_MONEY_STATUS_END = 0
BACK_MONEY_STATUS_NOW = 1
BACK_MONEY_STATUS_CN = {
    BACK_MONEY_STATUS_END: u'回款完成',
    BACK_MONEY_STATUS_NOW: u'正在回款',
}

direct_sales = db.Table('douban_order_direct_sales',
                        db.Column(
                            'direct_sale_id', db.Integer, db.ForeignKey('user.id')),
                        db.Column(
                            'douban_order_id', db.Integer, db.ForeignKey('bra_douban_order.id'))
                        )
agent_sales = db.Table('douban_order_agent_sales',
                       db.Column(
                           'agent_sale_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column(
                           'douban_order_id', db.Integer, db.ForeignKey('bra_douban_order.id'))
                       )

replace_sales = db.Table('douban_order_replace_sales',
                         db.Column(
                             'replace_sale_id', db.Integer, db.ForeignKey('user.id')),
                         db.Column(
                             'douban_order_id', db.Integer, db.ForeignKey('bra_douban_order.id'))
                         )

operater_users = db.Table('douban_order_users_operater',
                          db.Column(
                              'user_id', db.Integer, db.ForeignKey('user.id')),
                          db.Column(
                              'order_id', db.Integer, db.ForeignKey('bra_douban_order.id'))
                          )
designer_users = db.Table('douban_order_users_designerer',
                          db.Column(
                              'user_id', db.Integer, db.ForeignKey('user.id')),
                          db.Column(
                              'order_id', db.Integer, db.ForeignKey('bra_douban_order.id'))
                          )
planer_users = db.Table('douban_order_users_planer',
                        db.Column(
                            'user_id', db.Integer, db.ForeignKey('user.id')),
                        db.Column(
                            'order_id', db.Integer, db.ForeignKey('bra_douban_order.id'))
                        )


class DoubanOrder(db.Model, BaseModelMixin, CommentMixin, AttachmentMixin):
    __tablename__ = 'bra_douban_order'

    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'))  # 客户合同甲方
    agent = db.relationship(
        'Agent', backref=db.backref('douban_orders', lazy='dynamic'))
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))  # 客户
    client = db.relationship(
        'Client', backref=db.backref('douban_orders', lazy='dynamic'))
    campaign = db.Column(db.String(100))  # 活动名称

    contract = db.Column(db.String(100))  # 豆瓣合同号
    money = db.Column(db.Integer)  # 客户合同金额
    medium_CPM = db.Column(db.Integer)  # 实际CPM
    sale_CPM = db.Column(db.Integer)  # 下单CPM
    contract_type = db.Column(db.Integer)  # 合同类型： 标准，非标准
    client_start = db.Column(db.Date)
    client_end = db.Column(db.Date)
    reminde_date = db.Column(db.Date)  # 最迟回款日期

    direct_sales = db.relationship('User', secondary=direct_sales)
    agent_sales = db.relationship('User', secondary=agent_sales)
    replace_sales = db.relationship('User', secondary=replace_sales)

    operaters = db.relationship('User', secondary=operater_users)
    designers = db.relationship('User', secondary=designer_users)
    planers = db.relationship('User', secondary=planer_users)

    contract_status = db.Column(db.Integer)  # 合同审批状态
    status = db.Column(db.Integer)

    resource_type = db.Column(db.Integer)  # 资源形式
    sale_type = db.Column(db.Integer)  # 资源形式

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(
        'User', backref=db.backref('created_douban_orders', lazy='dynamic'))
    create_time = db.Column(db.DateTime)
    finish_time = db.Column(db.DateTime)   # 合同归档时间
    back_money_status = db.Column(db.Integer)

    contract_generate = False
    media_apply = False
    kind = "douban-order"
    __mapper_args__ = {'order_by': contract.desc()}

    def __init__(self, agent, client, campaign, status=STATUS_ON,
                 contract="", money=0, contract_type=CONTRACT_TYPE_NORMAL,
                 medium_CPM=0, sale_CPM=0, finish_time=None,
                 back_money_status=BACK_MONEY_STATUS_NOW,
                 client_start=None, client_end=None, reminde_date=None,
                 direct_sales=None, agent_sales=None, replace_sales=[],
                 operaters=None, designers=None, planers=None,
                 resource_type=RESOURCE_TYPE_AD, sale_type=SALE_TYPE_AGENT,
                 creator=None, create_time=None, contract_status=CONTRACT_STATUS_NEW):
        self.agent = agent
        self.client = client
        self.campaign = campaign

        self.contract = contract
        self.money = money
        self.contract_type = contract_type
        self.medium_CPM = medium_CPM
        self.sale_CPM = sale_CPM

        self.client_start = client_start or datetime.date.today()
        self.client_end = client_end or datetime.date.today()
        self.reminde_date = reminde_date or datetime.date.today()

        self.direct_sales = direct_sales or []
        self.agent_sales = agent_sales or []
        self.replace_sales = replace_sales

        self.operaters = operaters or []
        self.designers = designers or []
        self.planers = planers or []

        self.resource_type = resource_type
        self.sale_type = sale_type

        self.creator = creator
        self.create_time = create_time or datetime.datetime.now()
        self.finish_time = finish_time or datetime.datetime.now()
        self.contract_status = contract_status
        self.status = status
        self.back_money_status = back_money_status

    @classmethod
    def get_all(cls):
        """查看所有没删除订单"""
        return [o for o in cls.query.all() if o.status in [STATUS_ON, None] and o.contract_status not in [7, 8, 9]]

    @classmethod
    def all(cls):
        return cls.get_all()

    @classmethod
    def delete_all(cls):
        return [o for o in cls.query.all() if o.status == STATUS_DEL]

    @property
    def name(self):
        return u"%s-%s" % (self.client.name, self.campaign)

    @property
    def jiafang_name(self):
        return self.agent.name

    @property
    def sale_ECPM(self):
        return (self.money / self.sale_CPM) if self.sale_CPM else 0

    @property
    def locations(self):
        return list(set([u.location for u in self.direct_sales + self.agent_sales]))

    @property
    def locations_cn(self):
        return ",".join([TEAM_LOCATION_CN[l] for l in self.locations])

    @property
    def contract_type_cn(self):
        return CONTRACT_TYPE_CN[self.contract_type]

    @property
    def resource_type_cn(self):
        return RESOURCE_TYPE_CN.get(self.resource_type)

    @property
    def sale_type_cn(self):
        return SALE_TYPE_CN.get(self.sale_type)

    @property
    def direct_sales_names(self):
        return ",".join([u.name for u in self.direct_sales])

    @property
    def agent_sales_names(self):
        return ",".join([u.name for u in self.agent_sales])

    @property
    def replace_sales_names(self):
        return ",".join([u.name for u in self.replace_sales])

    @property
    def operater_names(self):
        return ",".join([u.name for u in self.operaters])

    @property
    def designers_names(self):
        return ",".join([u.name for u in self.designers])

    @property
    def planers_names(self):
        return ",".join([u.name for u in self.planers])

    @property
    def leaders(self):
        return list(set([l for u in self.direct_sales + self.agent_sales + self.replace_sales
                         for l in u.user_leaders] + User.super_leaders()))

    @property
    def operater_users(self):
        return [u for u in self.operaters]

    def can_admin(self, user):
        """是否可以修改该订单"""
        admin_users = self.direct_sales + self.agent_sales + [self.creator] + self.replace_sales
        return user.is_leader() or user.is_admin() or user.is_media_leader() or user in admin_users

    def path(self):
        return self.info_path()

    @property
    def start_date(self):
        return self.client_start

    @property
    def end_date(self):
        return self.client_end

    @property
    def start_date_cn(self):
        return self.start_date.strftime(DATE_FORMAT)

    @property
    def end_date_cn(self):
        return self.end_date.strftime(DATE_FORMAT)

    @property
    def reminde_date_cn(self):
        return self.reminde_date.strftime(DATE_FORMAT)

    @property
    def contract_status_cn(self):
        return CONTRACT_STATUS_CN[self.contract_status]

    @property
    def email_info(self):
        return u"""
        类型: 直签豆瓣订单
        客户: %s
        代理/直客: %s
        Campaign: %s
        金额: %s
        预估CPM: %s
        直客销售: %s
        渠道销售: %s
        执行: %s
        """ % (self.client.name, self.agent.name, self.campaign, self.money,
               self.sale_CPM or 0, self.direct_sales_names,
               self.agent_sales_names, self.operater_names)

    @property
    def search_info(self):
        return (self.client.name + self.agent.name +
                self.campaign + self.contract)

    def attachment_path(self):
        return url_for('files.douban_order_files', order_id=self.id)

    def info_path(self):
        return url_for("order.douban_order_info", order_id=self.id)

    def outsource_operater_info_path(self):
        return url_for("outsource.douban_orders")

    def outsource_info_path(self):
        return url_for("outsource.douban_outsources", order_id=self.id)

    def contract_path(self):
        return url_for("order.douban_order_contract", order_id=self.id)

    def attach_status_confirm_path(self, attachment):
        return url_for('order.douban_attach_status',
                       order_id=self.id,
                       attachment_id=attachment.id,
                       status=ATTACHMENT_STATUS_PASSED)

    def attach_status_reject_path(self, attachment):
        return url_for('order.douban_attach_status',
                       order_id=self.id,
                       attachment_id=attachment.id,
                       status=ATTACHMENT_STATUS_REJECT)

    def douban_contract_apply_path(self):
        return url_for("contract.douban_apply", order_id=self.id)

    @property
    def outsources(self):
        return [o for o in self.douban_outsources]

    def get_outsources_by_status(self, outsource_status):
        return [o for o in self.douban_outsources if o.status == outsource_status]

    def get_outsource_status_cn(self, status):
        from models.outsource import OUTSOURCE_STATUS_CN
        return OUTSOURCE_STATUS_CN[status]

    @property
    def outsources_sum(self):
        return sum([o.pay_num for o in self.douban_outsources if o.status != 0]) if self.douban_outsources else 0

    def apply_outsources(self):
        return [o for o in self.douban_outsources if o.status != 0]

    @property
    def outsources_paied_sum(self):
        return sum([o.pay_num for o in self.douban_outsources if o.status == 4]) if self.douban_outsources else 0

    @property
    def outsources_percent(self):
        return "%.1f" % (self.outsources_sum * 100 / float(self.money)) if self.money else "0"

    def delete(self):
        self.delete_comments()
        self.delete_attachments()
        db.session.delete(self)
        db.session.commit()

    def douban_contract_email_info(self, title):
        body = u"""
Dear %s:

%s

项目: %s
客户: %s
代理: %s
直客销售: %s
渠道销售: %s
时间: %s : %s
金额: %s

附注:
    致趣订单管理系统链接地址: %s

by %s\n
""" % (','.join([x.name for x in User.douban_contracts()]), title, self.campaign,
            self.client.name, self.jiafang_name,
            self.direct_sales_names, self.agent_sales_names,
            self.start_date_cn, self.end_date_cn,
            self.money, mail.app.config['DOMAIN'] + self.info_path(), g.user.name)
        return body

    @property
    def operater_ids(self):
        return ",".join([str(u.id) for u in self.operaters])

    def have_owner(self, user):
        """是否可以查看该订单"""
        owner = self.direct_sales + self.agent_sales + self.replace_sales +\
            [self.creator] + [k for k in self.operaters]
        return user.is_admin() or user in owner

    @classmethod
    def get_order_by_user(cls, user):
        """一个用户可以查看的所有订单"""
        return [o for o in cls.all() if o.have_owner(user) and o.status in [STATUS_ON, None]]

    def outsource_path(self):
        return url_for("outsource.douban_outsources", order_id=self.id)

    @property
    def outsource_info(self):
        return u"""
        客户订单总额:   %s 元
        外包应付总金额: %s 元
        外包占比:   %s %%""" % (self.money, self.outsources_sum, self.outsources_percent)

    def finance_outsource_path(self):
        return url_for("finance_pay.douban_info", order_id=self.id)

    def outsource_distribute_email_info(self, title):
        body = u"""
Dear %s:

%s

【直签豆瓣订单项目详情】
甲方: %s
项目: %s
客户: %s
合同号: %s
时间: %s : %s
金额: %s

【项目相关人员】
直客销售: %s
渠道销售: %s
运营: %s

附注:
    致趣订单管理系统链接地址: %s

by %s\n
""" % (self.operater_names, title, self.jiafang_name,
            self.campaign, self.client.name, self.contract,
            self.start_date_cn, self.end_date_cn, self.money,
            self.direct_sales_names, self.agent_sales_names,
            self.operater_names,
            mail.app.config['DOMAIN'] + self.outsource_info_path(), g.user.name)
        return body

    def outsource_email_info(self, to_user, title, o_info, url, msg):
        body = u"""

%s

【直签豆瓣订单项目详情】
甲方: %s
项目: %s
客户: %s
合同号: %s
时间: %s : %s
金额: %s
外包占比: %s %%

【外包组成】
%s

【项目相关人员】
直客销售: %s
渠道销售: %s
运营: %s

留言:
%s


附注:
    致趣订单管理系统链接地址: %s

by %s\n
""" % (title, self.jiafang_name,
            self.campaign, self.client.name, self.contract,
            self.start_date_cn, self.end_date_cn, self.money,
            self.outsources_percent, o_info,
            self.direct_sales_names, self.agent_sales_names,
            self.operater_names, msg, url, g.user.name)
        return body

    def order_agent_owner(self, user):
        """是否可以查看该订单"""
        owner = self.agent_sales
        return user in owner

    def order_direct_owner(self, user):
        """是否可以查看该订单"""
        owner = self.direct_sales
        return user in owner

    def pre_month_money(self):
        if self.money:
            pre_money = float(self.money) / \
                ((self.client_end - self.client_start).days + 1)
        else:
            pre_money = 0
        pre_month_days = get_monthes_pre_days(datetime.datetime.strptime(self.start_date_cn, '%Y-%m-%d'),
                                              datetime.datetime.strptime(self.end_date_cn, '%Y-%m-%d'))
        pre_month_money_data = []
        for k in pre_month_days:
            pre_month_money_data.append(
                {'money': '%.2f' % (pre_money * k['days']), 'month': k['month'], 'days': k['days']})
        return pre_month_money_data

    def is_executive_report(self):
        return DoubanOrderExecutiveReport.query.filter_by(douban_order=self).count() > 0

    def executive_report_data(self):
        pre_reports = DoubanOrderExecutiveReport.query.filter_by(
            douban_order=self)
        return [{'month_day': k.month_day, 'money': k.money} for k in pre_reports]

    def executive_report(self, user, now_year, monthes, sale_type):
        if sale_type == 'agent':
            count = len(self.agent_sales)
        else:
            count = len(self.direct_sales)
        if user.team.location == 3:
            count = len(self.agent_sales + self.direct_sales)
        if sale_type == 'normal':
            count = 1
        pre_reports = DoubanOrderExecutiveReport.query.filter_by(
            douban_order=self)
        moneys = []
        for j in monthes:
            try:
                pre_report = pre_reports.filter_by(
                    month_day=datetime.datetime(int(now_year), int(j), 1).date()).first()
            except:
                pre_report = None
            if pre_report:
                pre_money = pre_report.money
            else:
                pre_money = 0
            try:
                moneys.append(round(pre_money / count, 2))
            except:
                moneys.append(0)
        return moneys

    @property
    def agent_rebate(self):
        return self.agent.douban_rebate_by_year(self.client_start.year)

    def rebate_agent_by_month(self, year, month):
        rebate = self.agent.douban_rebate_by_year(self.client_start.year)
        ex_money = self.executive_report(g.user, year, [month], 'normal')[0]
        return round(ex_money * rebate / 100, 2)

    def rebate_money(self, year, month, type='profit'):
        rebate_money = 0
        if self.client_start.year == int(year) and self.client_start.month == int(month):
            rebate = self.agent.douban_rebate_by_year(self.client_start.year)
            if type == 'profit':
                rebate_money += self.money * (1 - rebate / 100)
            else:
                rebate_money += self.money * rebate / 100
        return rebate_money

    def income(self, year, month):
        if self.client_start.year == int(year) and self.client_start.month == int(month):
            return self.money * 0.4
        return 0

    def profit_money(self, year, month):
        return round(self.executive_report(g.user, year, [month], 'normal')[0] * 0.4 -
                     self.rebate_agent_by_month(year, month), 2)

    def get_saler_leaders(self):
        leaders = []
        for user in self.agent_sales + self.direct_sales:
            leaders += user.team_leaders
        return leaders

    def insert_reject_time(self):
        douban_order_reject = DoubanOrderReject.query.filter_by(
            douban_order=self, reject_time=datetime.date.today()).first()
        if douban_order_reject:
            douban_order_reject.reject_time = datetime.date.today()
        else:
            DoubanOrderReject.add(
                douban_order=self, reject_time=datetime.date.today())

    def zhixing_money(self, sale_type):
        try:
            if sale_type == 'agent':
                count = len(self.agent_sales)
                user = self.agent_sales[0]
            else:
                count = len(self.direct_sales)
                user = self.direct_sales[0]
            if user.team.location == 3:
                count = len(self.agent_sales + self.direct_sales)
            return self.money / count
        except:
            return 0

    @property
    def order_path(self):
        return url_for('order.douban_order_info', order_id=self.id)

    @property
    def back_moneys(self):
        return sum([k.money for k in self.douban_backmoneys] + [k.money for k in self.back_invoice_rebate_list])

    @property
    def client_back_moneys(self):
        return sum([k.money for k in self.douban_backmoneys])

    def back_moneys_by_Q(self, user, year, Q_monthes, sale_type):
        d = cal.monthrange(int(year), int(Q_monthes[-1]))
        start_month_day = datetime.datetime.strptime(
            str(year) + '-' + Q_monthes[0], '%Y-%m')
        last_month_day = datetime.datetime.strptime(
            str(year) + '-' + Q_monthes[-1] + '-' + str(d[1]) + ' 23:59', '%Y-%m-%d %H:%M')

        back_moneys = self.douban_backmoneys.filter(
            BackMoney.back_time <= last_month_day)
        t_b_moneys = sum([k.money for k in back_moneys])

        if sale_type == 'agent':
            count = len(self.agent_sales)
        else:
            count = len(self.direct_sales)
        if user.team.location == 3:
            count = len(self.agent_sales + self.direct_sales)

        pre_reports = DoubanOrderExecutiveReport.query.filter(
            DoubanOrderExecutiveReport.douban_order == self,
            DoubanOrderExecutiveReport.month_day < start_month_day)
        last_pre_reports = sum([k.money for k in pre_reports])
        if t_b_moneys <= last_pre_reports:
            return 0
        return (t_b_moneys - last_pre_reports) / count

    def last_back_moneys_time_by_Q(self, year, Q_monthes):
        d = cal.monthrange(int(year), int(Q_monthes[-1]))
        last_month_day = datetime.datetime.strptime(
            str(year) + '-' + Q_monthes[-1] + '-' + str(d[1]) + ' 23:59', '%Y-%m-%d %H:%M')
        last_back_time = self.douban_backmoneys.filter(
            BackMoney.back_time <= last_month_day).first()
        if last_back_time:
            return last_back_time.back_time_cn
        return u'无'

    @property
    def back_money_status_cn(self):
        if self.back_money_status == 0:
            return BACK_MONEY_STATUS_CN[BACK_MONEY_STATUS_END]
        else:
            return BACK_MONEY_STATUS_CN[self.back_money_status or 1]

    @property
    def back_money_percent(self):
        if self.back_money_status == 0:
            return 100
        else:
            return int(float(self.back_moneys) / self.money * 100) if self.money else 0

    @property
    def back_money_list(self):
        return self.douban_backmoneys

    @property
    def back_invoice_rebate_list(self):
        return self.douban_backinvoicerebates

    @property
    def back_invoice_rebate_money(self):
        return sum([k.money for k in self.douban_backinvoicerebates])

    def can_edit_contract_time(self, now_date=None):
        if not now_date:
            now_date = datetime.date.today()
        if self.client_start.month > now_date.month:
            return True
        else:
            return False

    @property
    def finish_time_cn(self):
        if self.contract_status == 20:
            try:
                return self.finish_time.date()
            except:
                return u'无'
        else:
            return u'无'


class DoubanOrderExecutiveReport(db.Model, BaseModelMixin):
    __tablename__ = 'bra_douban_order_executive_report'
    id = db.Column(db.Integer, primary_key=True)
    douban_order_id = db.Column(
        db.Integer, db.ForeignKey('bra_douban_order.id'))  # 客户合同
    douban_order = db.relationship(
        'DoubanOrder', backref=db.backref('douban_executive_reports', lazy='dynamic'))
    money = db.Column(db.Float())
    month_day = db.Column(db.DateTime)
    days = db.Column(db.Integer)
    create_time = db.Column(db.DateTime)
    __table_args__ = (db.UniqueConstraint(
        'douban_order_id', 'month_day', name='_douban_order_month_day'),)
    __mapper_args__ = {'order_by': month_day.desc()}

    def __init__(self, douban_order, money=0, month_day=None, days=0, create_time=None):
        self.douban_order = douban_order
        self.money = money
        self.month_day = month_day or datetime.date.today()
        self.days = days
        self.create_time = create_time or datetime.date.today()

    @property
    def month_cn(self):
        return self.month_day.strftime('%Y-%m') + u'月'

    @property
    def locations(self):
        return self.douban_order.locations

    @property
    def status(self):
        return self.douban_order.status


class DoubanOrderReject(db.Model, BaseModelMixin):
    __tablename__ = 'bra_douban_order_reject'
    id = db.Column(db.Integer, primary_key=True)
    douban_order_id = db.Column(
        db.Integer, db.ForeignKey('bra_douban_order.id'))  # 客户合同
    douban_order = db.relationship(
        'DoubanOrder', backref=db.backref('douban_order_reject_id', lazy='dynamic'))
    reject_time = db.Column(db.DateTime)
    __table_args__ = (db.UniqueConstraint(
        'douban_order_id', 'reject_time', name='_douban_order_reject_time'),)
    __mapper_args__ = {'order_by': reject_time.desc()}

    def __init__(self, douban_order, reject_time=None):
        self.douban_order = douban_order
        self.reject_time = reject_time or datetime.date.today()

    @property
    def reject_time_cn(self):
        return self.reject_time.strftime('%Y-%m') + u'月'


class BackMoney(db.Model, BaseModelMixin):
    __tablename__ = 'bra_douban_order_back_money'
    id = db.Column(db.Integer, primary_key=True)
    douban_order_id = db.Column(
        db.Integer, db.ForeignKey('bra_douban_order.id'))  # 客户合同
    douban_order = db.relationship(
        'DoubanOrder', backref=db.backref('douban_backmoneys', lazy='dynamic'))
    money = db.Column(db.Float())
    back_time = db.Column(db.DateTime)
    create_time = db.Column(db.DateTime)
    __mapper_args__ = {'order_by': create_time.desc()}

    def __init__(self, douban_order, money=0.0, create_time=None, back_time=None):
        self.douban_order = douban_order
        self.money = money
        self.create_time = create_time or datetime.date.today()
        self.back_time = back_time or datetime.date.today()

    @property
    def back_time_cn(self):
        return self.back_time.strftime(DATE_FORMAT)

    @property
    def create_time_cn(self):
        return self.create_time.strftime(DATE_FORMAT)


class BackInvoiceRebate(db.Model, BaseModelMixin):
    __tablename__ = 'bra_douban_order_back_invoice_rebate'
    id = db.Column(db.Integer, primary_key=True)
    douban_order_id = db.Column(
        db.Integer, db.ForeignKey('bra_douban_order.id'))  # 客户合同
    douban_order = db.relationship(
        'DoubanOrder', backref=db.backref('douban_backinvoicerebates', lazy='dynamic'))
    num = db.Column(db.String(100))  # 发票号
    money = db.Column(db.Float())
    back_time = db.Column(db.DateTime)
    create_time = db.Column(db.DateTime)
    __mapper_args__ = {'order_by': create_time.desc()}

    def __init__(self, douban_order, num='', money=0.0, create_time=None, back_time=None):
        self.douban_order = douban_order
        self.num = num
        self.money = money
        self.create_time = create_time or datetime.date.today()
        self.back_time = back_time or datetime.date.today()

    @property
    def back_time_cn(self):
        return self.back_time.strftime(DATE_FORMAT)

    @property
    def create_time_cn(self):
        return self.create_time.strftime(DATE_FORMAT)
