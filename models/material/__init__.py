# -*- coding: UTF-8 -*-
import json
from flask import url_for, render_template
from sqlalchemy.ext.mutable import MutableDict

from models import db, BaseModelMixin
from models.consts import STATUS_CN
from models.mixin.comment import CommentMixin
from models.mixin.delivery import DeliveryMixin
from libs.files import get_full_path

MATERIAL_TYPE_RAW = 0
MATERIAL_TYPE_PICTURE = 1
MATERIAL_TYPE_PICTUREANDTEXT = 2
MATERIAL_TYPE_VIDEO = 3

MATERIAL_TYPE_CN = {
    MATERIAL_TYPE_RAW: u"原生广告",
    MATERIAL_TYPE_PICTURE: u"图片广告",
    MATERIAL_TYPE_PICTUREANDTEXT: u"图文广告",
    MATERIAL_TYPE_VIDEO: u"视频广告",
}


class Material(db.Model, BaseModelMixin, CommentMixin, DeliveryMixin):
    __tablename__ = 'materials'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.Integer)
    item_id = db.Column(db.Integer, db.ForeignKey('bra_item.id'))
    item = db.relationship('AdItem', backref=db.backref('materials', lazy='dynamic', enable_typechecks=False))
    code = db.Column(db.Text())  # 原生广告代码
    props = db.Column(MutableDict.as_mutable(db.PickleType(pickler=json)))  # 广告属性, 一个字典, PikleType可以存储大部分 Python 实例
    status = db.Column(db.Integer, default=1)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref=db.backref('created_material', lazy='dynamic', enable_typechecks=False))

    def __init__(self, name, item, creator, type=MATERIAL_TYPE_RAW):
        self.name = name
        self.type = type
        self.item = item
        self.creator = creator
        self.props = {}

    def __repr__(self):
        return '<Material %s>' % (self.name)

    @property
    def type_cn(self):
        return MATERIAL_TYPE_CN[self.type]
        
    @property
    def status_cn(self):
        return STATUS_CN[self.status]

    @property
    def width(self):
        return self.item.position.size.width

    @property
    def height(self):
        return self.item.position.size.height

    def path(self):
        if self.type == MATERIAL_TYPE_PICTURE:
            return url_for('material.image_material', material_id=self.id)
        else:
            return url_for('material.raw_material', material_id=self.id)

    @property
    def html(self):
        return self.code

    @property
    def processed_html(self):
        if self.html:
            return self.html.replace("%%CLICK%%", "")  # 预览的时候, 去掉CLICK宏

    @property
    def get_ctr(self):
        return (str(round(float(self.get_click_num_all()) / float(self.get_monitor_num_all()),
                    2) * 100) + '%') if self.get_monitor_num_all() else 0.0

    @property
    def preview_path(self):
        if self.type == MATERIAL_TYPE_PICTURE:
            return url_for('material.image_preview', material_id=self.id)
        else:
            return url_for('material.raw_preview', material_id=self.id)

    def is_online_by_date(self, _date):
        """该日期是否有投放"""
        return self.item.is_online_by_date(_date)

    @classmethod
    def online_materials(cls, _date):
        return [m for m in cls.all() if m.is_online_by_date(_date)]


class ImageMaterial(Material):

    def __init__(self, name, item, creator):
        self.name = name
        self.type = MATERIAL_TYPE_PICTURE
        self.item = item
        self.creator = creator
        self.props = {}

    def save(self):
        self.code = self.html
        db.session.commit()

    @property
    def image_file(self):
        return self.props.get('image_file', '')

    @image_file.setter
    def image_file(self, filename):
        self.props['image_file'] = filename
        self.save()

    @property
    def image_link(self):
        return get_full_path(self.image_file)

    @property
    def click_link(self):
        return self.props.get('image_click', '')

    @click_link.setter
    def click_link(self, link):
        self.props['image_click'] = link
        self.save()

    @property
    def monitor_link(self):
        return self.props.get('image_monitor', '')

    @monitor_link.setter
    def monitor_link(self, link):
        self.props['image_monitor'] = link
        self.save()

    @property
    def html(self):
        context = {'image_link': self.image_link,
                   'click_link': self.click_link,
                   'monitor_link': self.monitor_link,
                   'width': self.width,
                   'height': self.height}
        rt = render_template('/material_tpl/image.html', **context)
        return rt
