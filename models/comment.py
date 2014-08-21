#-*- coding: UTF-8 -*-
import datetime

from . import db, BaseModelMixin


class Comment(db.Model, BaseModelMixin):
    __tablename__ = 'bra_comment'
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.String(100))
    msg = db.Column(db.String(1000))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, owner, msg, creator, create_time=datetime.datetime.now()):
        self.owner = owner
        self.msg = msg
        self.creator = creator
        self.create_time = create_time

    def __repr__(self):
        return '<Comment %s>' % (self.id)


class CommentMixin():

    @property
    def comment_identify(self):
        return "%s:%s" % (self.__class__.__name__, self.id)

    def add_comment(self, user, msg):
        comment = Comment(self.comment_identify, msg, user, datetime.datetime.now())
        comment.add()

    def get_comments(self):
        return Comment.query.filter_by(owner=self.comment_identify).order_by(Comment.create_time)
