# Moderator feature tests
import sys
import os
import pytest
from moj import create_app
from moj.db import init_db, get_db
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def login_user(client, email='user@example.com', nickname='user', password='pass'):
    client.post('/auth/register', data={
        'email': email,
        'nickname': nickname,
        'password': password
    })
    client.post('/auth/login', data={
        'identifier': nickname,
        'password': password
    })


def login_moderator(client):
    login_user(client, email='mod@example.com', nickname='moderator', password='modpass')
    with client.application.app_context():
        db = get_db()
        db.execute("UPDATE user SET role = 'moderator' WHERE email = ?", ('mod@example.com',))
        db.commit()


def test_moderator_dashboard_access(client):
    login_moderator(client)
    rv = client.get('/moderator/dashboard')
    assert b'Welcome, Moderator!' in rv.data


def test_manage_users_listing(client, app):
    login_moderator(client)
    response = client.get("/moderator/manage-users")
    assert b"moderator" in response.data

def test_moderator_promote_user(client):
    login_moderator(client)

    with client.application.app_context():
        db = get_db()
        db.execute("INSERT INTO user (email, nickname, password, role) VALUES (?, ?, ?, ?)",
                   ('target@example.com', 'targetuser', 'pass', 'user'))
        db.commit()

    rv = client.post('/moderator/manage-users', data={
        'action': 'promote',
        'user_id': 2
    }, follow_redirects=True)

    assert b'User promoted to moderator' in rv.data


def test_moderator_demote_user(client):
    login_moderator(client)

    with client.application.app_context():
        db = get_db()
        db.execute("INSERT INTO user (email, nickname, password, role) VALUES (?, ?, ?, ?)",
                   ('target@example.com', 'targetmod', 'pass', 'moderator'))
        db.commit()

    rv = client.post('/moderator/manage-users', data={
        'action': 'demote',
        'user_id': 2
    }, follow_redirects=True)

    assert b'Moderator demoted to user' in rv.data


def test_non_mod_cannot_access_dashboard(client):
    login_user(client)
    rv = client.get('/moderator/dashboard', follow_redirects=True)
    assert b'Unauthorized access' in rv.data


def test_cannot_demote_last_moderator(client):
    login_moderator(client)

    with client.application.app_context():
        db = get_db()        
        db.execute("DELETE FROM user WHERE role = 'moderator' AND email != ?", ('mod@example.com',))
        db.commit()

        moderator_id = db.execute("SELECT id FROM user WHERE email = ?", ('mod@example.com',)).fetchone()['id']

    rv = client.post('/moderator/manage-users', data={
        'action': 'demote',
        'user_id': moderator_id
    }, follow_redirects=True)

    assert b'Cannot remove the last moderator' in rv.data


def login_moderator(client):
    client.post('/auth/register', data={
        'email': 'mod@example.com',
        'nickname': 'moddy',
        'password': 'pass123'
    })
    with client.application.app_context():
        db = get_db()
        db.execute("UPDATE user SET role = 'moderator' WHERE email = ?", ('mod@example.com',))
        db.commit()
    client.post('/auth/login', data={
        'identifier': 'moddy',
        'password': 'pass123'
    })

def test_moderator_update_balance(client):
    login_moderator(client)

    with client.application.app_context():
        db = get_db()
        db.execute("INSERT INTO user (email, nickname, password, joke_balance) VALUES (?, ?, ?, ?)",
                   ('user@example.com', 'normaluser', 'pass123', 1))
        db.commit()
        user_id = db.execute("SELECT id FROM user WHERE email = ?", ('user@example.com',)).fetchone()['id']

    rv = client.post(f'/moderator/update-balance/{user_id}', data={'balance': 5}, follow_redirects=True)
    
    assert b'Updated balance for user ID' in rv.data

    with client.application.app_context():
        db = get_db()
        updated_balance = db.execute("SELECT joke_balance FROM user WHERE id = ?", (user_id,)).fetchone()['joke_balance']
        assert updated_balance == 5
