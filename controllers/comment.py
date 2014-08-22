#-*- coding: UTF-8 -*-
from flask import Blueprint, request, g, jsonify

from models.comment import Comment

comment_bp = Blueprint('comment', __name__)


@comment_bp.route('/add/', methods=['POST'])
def add():
    target_type = request.values.get('target_type')
    target_id = request.values.get('target_id')
    msg = request.values.get('msg')
    comment = Comment(target_type, target_id, msg, g.user)
    comment.add()
    return jsonify({'msg': "msg add success"})
