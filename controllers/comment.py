# -*- coding: UTF-8 -*-
from flask import Blueprint, request, g, jsonify, current_app

from models.comment import Comment
from libs.signals import add_comment_signal

comment_bp = Blueprint('comment', __name__)


@comment_bp.route('/add/', methods=['POST'])
def add():
    target_type = request.values.get('target_type')
    target_id = request.values.get('target_id')
    msg = request.values.get('msg')
    comment = Comment.add(target_type, target_id, msg, g.user)
    add_comment_signal.send(current_app._get_current_object(), comment=comment)
    return jsonify({'msg': "msg add success"})
