#-*- coding: UTF-8 -*-
import re
from jinja2 import evalcontextfilter, Markup, escape

from models.item import ITEM_STATUS_ACTION_CN

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')


def item_status_action_cn(action):
    return ITEM_STATUS_ACTION_CN[action]


@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n')
                          for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result

def format_price(amount, currency=u'￥'):
    n = float('{0:.2f}'.format(amount))
    return u'{1}{0:,}'.format(n, currency)


def register_filter(app):
    env = app.jinja_env
    env.filters['item_status_action_cn'] = item_status_action_cn
    env.filters['nl2br'] = nl2br
    env.filters['format_price'] = format_price
