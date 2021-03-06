# -*- coding: UTF-8 -*-
from flask import Blueprint, request, g, jsonify, current_app

from models.comment import Comment
from libs.email_signals import add_comment_signal

comment_bp = Blueprint('comment', __name__)


@comment_bp.route('/add/', methods=['POST'])
def add():
    target_type = request.values.get('target_type')
    target_id = request.values.get('target_id')
    url = request.values.get('url')
    msg = request.values.get('msg')
    msg_channel = request.values.get('msg_channel')
    comment = Comment.add(target_type, target_id, msg, g.user, msg_channel=msg_channel)
    add_comment_signal.send(current_app._get_current_object(), comment=comment, msg_channel=msg_channel, url=url)
    return jsonify({'msg': "msg add success"})
