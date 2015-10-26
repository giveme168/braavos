from urls.data_query import data_query_register_blueprint
from urls.user import user_register_blueprint
from urls.client import client_register_blueprint
from urls.medium import medium_register_blueprint
from urls.order import order_register_blueprint
from urls.schedule import schedule_register_blueprint
from urls.comments import comments_register_blueprint
from urls.material import materia_register_blueprint
from urls.files import files_register_blueprint
from urls.api import api_register_blueprint
from urls.storage import storage_register_blueprint
from urls.contract import contract_register_blueprint
from urls.outsource import outsource_register_blueprint
from urls.saler import saler_register_blueprint
from urls.finance import finance_register_blueprint
from urls.util import util_register_blueprint
from urls.mediums import mediums_register_blueprint
from urls.account import account_register_blueprint
from urls.planning import planning_register_blueprint
# for searchAd team
from urls.searchAd.order import searchAd_order_register_blueprint
from urls.searchAd.client import searchAd_client_register_blueprint
from urls.searchAd.saler import searchAd_saler_register_blueprint
from urls.searchAd.finance import searchAd_finance_register_blueprint


def register_blueprint(app):
    user_register_blueprint(app)
    data_query_register_blueprint(app)
    client_register_blueprint(app)
    medium_register_blueprint(app)
    order_register_blueprint(app)
    comments_register_blueprint(app)
    materia_register_blueprint(app)
    files_register_blueprint(app)
    api_register_blueprint(app)
    storage_register_blueprint(app)
    contract_register_blueprint(app)
    outsource_register_blueprint(app)
    saler_register_blueprint(app)
    finance_register_blueprint(app)
    schedule_register_blueprint(app)
    util_register_blueprint(app)
    mediums_register_blueprint(app)
    account_register_blueprint(app)
    planning_register_blueprint(app)
    searchAd_order_register_blueprint(app)
    searchAd_client_register_blueprint(app)
    searchAd_saler_register_blueprint(app)
    searchAd_finance_register_blueprint(app)
