#-*- coding: utf-8 -*-
from libs.db import db


class BaseModelMixin():

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def save(self):
        db.session.commit()

    @classmethod
    def get(cls, model_id):
        return cls.query.filter_by(id=model_id).first()

    @classmethod
    def gets(cls, model_ids):
        return [cls.get(id) for id in model_ids]

    @classmethod
    def all(cls):
        return cls.query.all()
