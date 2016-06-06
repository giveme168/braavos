from __future__ import with_statement
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
from models.user import User, Team
from models.client import Client, Group, Agent, AgentRebate
from models.comment import Comment
from models.attachment import Attachment
from models.item import AdItem, AdSchedule
from models.material import Material
from models.medium import Medium, MediumRebate, AdSize, AdUnit, AdPosition
from models.order import Order
from models.client_order import ClientOrder
from models.framework_order import FrameworkOrder
from models.douban_order import DoubanOrder
from models.associated_douban_order import AssociatedDoubanOrder
from models.delivery import Delivery
from models.outsource import OutSourceTarget, OutSource
from models.invoice import Invoice, AgentInvoice, AgentInvoicePay, \
    MediumInvoice, MediumInvoicePay, MediumRebateInvoice
from models.account.saler import *
# target_metadata = mymodel.Base.metadata
# models for searchAd
from searchAd.models.client import searchAdClient, searchAdGroup, searchAdAgent, searchAdAgentRebate
from searchAd.models.medium import searchAdMedium, searchAdMediumRebate
from searchAd.models.client_order import searchAdClientOrder
from searchAd.models.order import searchAdOrder
from searchAd.models.invoice import searchAdInvoice, searchAdAgentInvoice, searchAdAgentInvoicePay, \
    searchAdMediumInvoice, searchAdMediumInvoicePay, searchAdMediumRebateInvoice
from searchAd.models.framework_order import *
from models.account.data import *
from models.other import *
from models.client_medium_order import *
from flask import current_app
config.set_main_option('sqlalchemy.url', current_app.config.get('SQLALCHEMY_DATABASE_URI'))
target_metadata = current_app.extensions['migrate'].db.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    engine = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool)

    connection = engine.connect()
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
