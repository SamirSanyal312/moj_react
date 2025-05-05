# Auth tests
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import tempfile
from moj import create_app
from moj.db import init_db, get_db

@pytest.fixture
def client():
    
    db_fd, db_path = tempfile.mkstemp()

    app = create_app()
    app.config.update({
        'TESTING': True,
        'DATABASE': db_path 
    })

    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client

def test_register(client):
    rv = client.post('/auth/register', data={
        'email': 'test@example.com',
        'nickname': 'tester',
        'password': 'password'
    }, follow_redirects=True)
    assert b'Login' in rv.data

def test_login(client):
    rv = client.post('/auth/login', data={
        'identifier': 'tester',
        'password': 'password'
    }, follow_redirects=True)
    assert b'Master of Jokes' in rv.data

def test_logout(client):
    rv = client.get('/auth/logout', follow_redirects=True)
    assert b'Login' in rv.data


def test_database_insert(client):
    with client.application.app_context():
        db = get_db()
        db.execute('INSERT INTO user (email, nickname, password) VALUES (?, ?, ?)',
                   ('x@y.com', 'xnick', 'xpass'))
        db.commit()
        user = db.execute('SELECT * FROM user WHERE email = ?', ('x@y.com',)).fetchone()
        assert user['nickname'] == 'xnick'