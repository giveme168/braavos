#-*- coding: UTF-8 -*-
from . import db, BaseModelMixin

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


class Material(db.Model, BaseModelMixin):
    __tablename__ = 'materials'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.Integer)
    item_id = db.Column(db.Integer, db.ForeignKey('bra_item.id'))
    item = db.relationship('AdItem', backref=db.backref('materials', lazy='dynamic'))
    code = db.Column(db.Text())  # 原生广告代码
    props = db.Column(db.PickleType())  # 广告属性, 一个字典, PikleType可以存储大部分 Python 实例
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref=db.backref('created_material', lazy='dynamic'))

    def __init__(self, name, type, item, creator, code="", props={}):
        self.name = name
        self.type = type
        self.item = item
        self.creator = creator
        self.code = code
        self.props = props

    def __repr__(self):
        return '<Material %s>' % (self.name)

    @property
    def type_cn(self):
        return MATERIAL_TYPE_CN[self.type]
