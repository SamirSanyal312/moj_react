# tests/conftest.py
import os
import tempfile

import pytest
from moj import create_app
from moj.db import init_db, get_db

with open(os.path.join(os.path.dirname(__file__), '..', 'moj', 'schema.sql'), 'rb') as f:
    _schema_sql = f.read().decode('utf8')

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    # app = create_app() 
    # app.config['TESTING'] = True
    # app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"  # In-memory database        

    app = create_app()
    app.config.update({
        'TESTING': True,
        'DATABASE': db_path  # Tell your app to use this file
    })

    with app.app_context():
        init_db()
        print("Database schema applied successfully in conftest.py")        
        get_db().executescript(_schema_sql)


    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

def test_init_db_command(runner):
    result = runner.invoke(args=['init-db'])
    assert b'Initialized' in result.output