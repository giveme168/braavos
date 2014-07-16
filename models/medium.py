#-*- coding: UTF-8 -*-
from . import db, BaseModelMixin


class Medium(db.Model, BaseModelMixin):
    __tablename__ = 'medium'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    owner_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    owner = db.relationship('Team', backref=db.backref('mediums', lazy='dynamic'))

    def __init__(self, name, owner):
        self.name = name.title()
        self.owner = owner

    def __repr__(self):
        return '<Medium %s>' % (self.name)
