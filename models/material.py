#-*- coding: UTF-8 -*-
from flask import url_for

from . import db, BaseModelMixin
from .consts import STATUS_CN
from models.mixin.comment import CommentMixin

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


class Material(db.Model, BaseModelMixin, CommentMixin):
    __tablename__ = 'materials'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.Integer)
    item_id = db.Column(db.Integer, db.ForeignKey('bra_item.id'))
    item = db.relationship('AdItem', backref=db.backref('materials', lazy='dynamic', enable_typechecks=False))
    code = db.Column(db.Text())  # 原生广告代码
    props = db.Column(db.PickleType())  # 广告属性, 一个字典, PikleType可以存储大部分 Python 实例
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

    def path(self):
        if self.type == MATERIAL_TYPE_PICTURE:
            return url_for('material.image_material', material_id=self.id)
        else:
            return url_for('material.raw_material', material_id=self.id)


class ImageMaterial(Material):

    def __init__(self, name, item, creator):
        self.name = name
        self.type = MATERIAL_TYPE_PICTURE
        self.item = item
        self.creator = creator
        self.props = {}

    @property
    def image_link(self):
        return self.props.get('image_link', '')

    @image_link.setter
    def image_link(self, link):
        self.props['image_link'] = link

    @property
    def click_link(self):
        return self.props.get('image_click', '')

    @click_link.setter
    def click_link(self, link):
        self.props['image_click'] = link

    @property
    def monitor_link(self):
        return self.props.get('image_monitor', '')

    @monitor_link.setter
    def monitor_link(self, link):
        self.props['image_monitor'] = link
