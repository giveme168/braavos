# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request
from flask import render_template as tpl

from models.medium import Medium
from libs.paginator import Paginator
from controllers.data_query.helpers.medium_helpers import write_client_excel


data_query_medium_bp = Blueprint(
    'data_query_medium', __name__, template_folder='../../templates/data_query')


@data_query_medium_bp.route('/', methods=['GET'])
def index():
    page = int(request.values.get('p', 1))
    medium_id = int(request.values.get('medium_id', 0))
    if medium_id:
        mediums = Medium.query.filter_by(id=medium_id)
    else:
        mediums = Medium.all()
    if request.values.get('action', '') == 'download':
        return write_client_excel(mediums)
    paginator = Paginator(list(mediums), 50)
    try:
        mediums = paginator.page(page)
    except:
        mediums = paginator.page(paginator.num_pages)
    return tpl('/data_query/medium/index.html', mediums=mediums, medium_id=medium_id,
               now_date=datetime.datetime.now(), page=page,
               params="&medium_id=%s" % (medium_id), s_mediums=Medium.all())
