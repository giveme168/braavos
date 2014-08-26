#-*- coding: utf-8 -*-
from libs.db import db


class BaseModelMixin(object):

    @classmethod
    def add(cls, *args, **kwargs):
        _instance = cls(*args, **kwargs)
        db.session.add(_instance)
        db.session.commit()
        return _instance

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def save(self):
        db.session.commit()

    @classmethod
    def get(cls, model_id):
        return cls.query.get(model_id)

    @classmethod
    def gets(cls, model_ids):
        return [cls.get(id) for id in model_ids]

    @classmethod
    def all(cls):
        return cls.query.all()
