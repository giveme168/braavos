# -*- coding: UTF-8 -*-
from flask import Blueprint, request, g, jsonify

from models.comment import Comment

comment_bp = Blueprint('comment', __name__)


@comment_bp.route('/add/', methods=['POST'])
def add():
    from libs.sendcloud import add_comment
    target_type = request.values.get('target_type')
    target_id = request.values.get('target_id')
    msg = request.values.get('msg')
    msg_channel = request.values.get('msg_channel')
    comment = Comment.add(target_type, target_id, msg, g.user, msg_channel=msg_channel)
    add_comment(g.user, comment)
    return jsonify({'msg': "msg add success"})
