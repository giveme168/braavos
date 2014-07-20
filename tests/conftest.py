import pytest
from braavos.factory import create_app
from braavos.libs.db import db as _db


@pytest.fixture(scope='session')
def app(request):
    app = create_app("braavos.config.TestingConfig")

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database."""
    def teardown():
        _db.drop_all()

    _db.app = app
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session

'''
from sqlalchemy import create_engine
from braavos.libs.db import db


@pytest.fixture(scope='session')
def connection(request):
    engine = create_engine('postgresql://localhost/test_bar')
    db.Base.metadata.create_all(engine)
    connection = engine.connect()
    db.session.registry.clear()
    db.session.configure(bind=connection)
    db.Base.metadata.bind = engine
    request.addfinalizer(db.Base.metadata.drop_all)
    return connection


@pytest.fixture
def db_session(request, connection):
    from transaction import abort
    trans = connection.begin()
    request.addfinalizer(trans.rollback)
    request.addfinalizer(abort)

    return db.session
'''
