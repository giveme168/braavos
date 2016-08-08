# encoding: utf-8
import sys
sys.path.append('/Users/guoyu1/workspace/inad/braavos')
# sys.path.append('/home/inad/apps/braavos/releases/current')

from app import app

from models.client_order import IntentionOrder
from models.client_medium_order import ClientMediumOrder
from models.order import Order
from models.medium import Medium, Media, Case
from models.invoice import MediumRebateInvoice
from models.medium_framework_order import MediumFrameworkOrder
from models.attachment import Attachment
from models.invoice import MediumRebateInvoice, MediumInvoice


def fix_intention_data():
    intentions = IntentionOrder.all()
    for i in intentions:
        if i.medium_id == 0:
            i.media_id = 0
        else:
            medium = Medium.get(i.medium_id)
            i.media_id = Media.query.filter_by(name=medium.name).first().id
        i.save()
    return


def fix_order_data():
    orders = Order.all()
    for o in orders:
        try:
            o.media = Media.query.filter_by(name=o.medium.name).first()
            o.save()
        except:
            print o.id
    return


def fix_client_medium_order_data():
    orders = ClientMediumOrder.all()
    for o in orders:
        o.media = Media.query.filter_by(name=o.medium.name).first()
        o.save()
    return


def fix_medium_rebate_invoice_data():
    invoices = MediumRebateInvoice.all()
    for i in invoices:
        i.media = Media.query.filter_by(name=i.medium.name).first()
        i.save()
    return


def fix_medium_framework_order_data():
    orders = MediumFrameworkOrder.all()
    for o in orders:
        o.medium_groups = list(set([m.medium_group for m in o.mediums]))
        o.save()


def fix_medium_att_data():
    atts = [a for a in Attachment.query.filter_by(target_type='Medium') if a.attachment_type in [5, 6, 7, 8]]
    for a in atts:
        a.target_type = 'Media'
        medium = Medium.get(a.target_id)
        media = Media.query.filter_by(name=medium.name).first()
        if media:
            a.target_id = media.id
        a.save()


def fix_case_data():
    cases = Case.all()
    for k in cases:
        medias = []
        for m in k.mediums:
            media = Media.query.filter_by(name=m.name).first()
            if media:
                medias.append(media)
        k.medias = medias
        k.save()


def fix_medium_invoice_data():
    re_invoice = MediumRebateInvoice.all()
    med_invoice = MediumInvoice.all()
    for r in re_invoice:
        medias = [k for k in Media.all() if k.name.lower() == r.medium.name.lower()]
        r.medium_group = r.medium.medium_group
        r.media = medias[0]
        r.save()

    for r in med_invoice:
        medias = [k for k in Media.all() if k.name.lower() == r.medium.name.lower()]
        r.medium_group = r.medium.medium_group
        r.media = medias[0]
        r.save()

if __name__ == '__main__':
    fix_medium_invoice_data()
