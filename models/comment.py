#-*- coding: UTF-8 -*-
import datetime

from . import db, BaseModelMixin


class Comment(db.Model, BaseModelMixin):
    __tablename__ = 'bra_comment'
    id = db.Column(db.Integer, primary_key=True)
    target_type = db.Column(db.String(50))
    target_id = db.Column(db.Integer)
    msg = db.Column(db.String(1000))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, target_type, target_id, msg, creator,
                 create_time=None):
        self.target_type = target_type
        self.target_id = target_id
        self.msg = msg
        self.creator = creator
        self.create_time = create_time

    def __repr__(self):
        return '<Comment %s, target:%s-%s>' % (self.id, self.target_type, self.target_id)


class CommentMixin():

    @property
    def target_type(self):
        return self.__class__.__name__

    @property
    def target_id(self):
        return self.id

    def add_comment(self, user, msg):
        comment = Comment(self.target_type, self.target_id, msg, user, datetime.datetime.now())
        comment.add()

    def get_comments(self):
        return Comment.query.filter_by(target_type=self.target_type,
                                       target_id=self.target_id).order_by(Comment.create_time)
