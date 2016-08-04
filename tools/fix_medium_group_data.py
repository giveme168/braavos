# encoding: utf-8
import sys
sys.path.append('/Users/guoyu1/workspace/inad/braavos')
# sys.path.append('/home/inad/apps/braavos/releases/current')

from app import app

from models.client_order import IntentionOrder
from models.client_medium_order import ClientMediumOrder
from models.order import Order
from models.medium import Medium
from models.invoice import MediumRebateInvoice


def fix_intention_data():
    intentions = IntentionOrder.all()
    for i in intentions:
        if i.medium_id == 0:
            i.medium_group_id = 0
        else:
            i.medium_group_id = Medium.get(i.medium_id).medium_group_id
        i.save()
    return


def fix_order_data():
    orders = Order.all()
    for o in orders:
        o.medium_group = o.medium.medium_group
        o.save()
    return


def fix_client_medium_order_data():
    orders = ClientMediumOrder.all()
    for o in orders:
        o.medium_group = o.medium.medium_group
        o.save()
    return


def fix_medium_rebate_invoice_data():
    invoices = MediumRebateInvoice.all()
    for i in invoices:
        i.medium_group = i.medium.medium_group
        i.save()
    return


if __name__ == '__main__':
    fix_intention_data()
    fix_order_data()
    fix_client_medium_order_data()
    fix_medium_rebate_invoice_data()
