#-*- coding: UTF-8 -*-
from flask import Blueprint, request, g, jsonify

from models.comment import Comment

comment_bp = Blueprint('comment', __name__)


@comment_bp.route('/add/', methods=['POST'])
def add():
    identify = request.values.get('identify')
    msg = request.values.get('msg')
    comment = Comment(identify, msg, g.user)
    comment.add()
    return jsonify({'msg': "msg add success"})
