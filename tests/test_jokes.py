# Jokes feature tests
import sys
import os
import re
import pytest
from moj import create_app
from moj.db import init_db, get_db
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def login(client):
    client.post('/auth/register', data={
        'email': 'joke@example.com',
        'nickname': 'joker',
        'password': 'pass123'
    })
    client.post('/auth/login', data={
        'identifier': 'joker',
        'password': 'pass123'
    })

def test_leave_joke(client):
    login(client)
    rv = client.post('/joke/leave', data={
        'title': 'Short Joke',
        'body': 'Why did the chicken cross the road?'
    }, follow_redirects=True)
    assert b'Joke added successfully!' in rv.data

def test_no_title_leave_joke(client):
    login(client)
    rv = client.post('/joke/leave', data={
        'title': '',
        'body': 'Why is there no title?'
    }, follow_redirects=True)
    assert b'Title is required.' in rv.data


def test_long_title_leave_joke(client):
    login(client)
    rv = client.post('/joke/leave', data={
        'title': 'This is an example of a title with more than ten words!',
        'body': 'Why is the title so long?'
    }, follow_redirects=True)
    assert b'Title must be no more than 10 words.' in rv.data

def test_leave_title_again_joke(client):
    login(client)
    rv = client.post('/joke/leave', data={
        'title': 'My joke of the day!',
        'body': 'LoL Rofl LMAO!'
    }, follow_redirects=True)
    rv = client.post('/joke/leave', data={
        'title': 'My joke of the day!',
        'body': 'Haha Hohoho!'
    }, follow_redirects=True)
    assert b'You already used this title' in rv.data


def test_successful_take_joke(client):
    login(client)
    
    client.post('/joke/leave', data={
        'title': 'My own joke',
        'body': 'It is hilarious'
    })

    with client.application.app_context():
        db = get_db()        
        db.execute("INSERT INTO user (email, nickname, password) VALUES (?, ?, ?)",
                   ('other@example.com', 'otherguy', 'pass'))
        other_user_id = db.execute("SELECT id FROM user WHERE email = ?", 
                                   ('other@example.com',)).fetchone()['id']
        db.execute("INSERT INTO joke (title, body, author_id) VALUES (?, ?, ?)",
                   ('Another Joke', 'Haha', other_user_id))
        db.commit()
        joke_id = db.execute("SELECT id FROM joke WHERE title = ?", 
                             ('Another Joke',)).fetchone()['id']

    rv = client.post('/joke/take', data={'joke_id': joke_id}, follow_redirects=True)

    assert b'You have successfully taken this joke!' in rv.data

def test_twice_take_joke(client):
    login(client)
    
    client.post('/joke/leave', data={
        'title': 'My own joke',
        'body': 'It is hilarious'
    })
    client.post('/joke/leave', data={
        'title': 'My own joke again',
        'body': 'It is hilarious twice'
    })

    with client.application.app_context():
        db = get_db()        
        db.execute("INSERT INTO user (email, nickname, password) VALUES (?, ?, ?)",
                   ('other@example.com', 'otherguy', 'pass'))
        other_user_id = db.execute("SELECT id FROM user WHERE email = ?", 
                                   ('other@example.com',)).fetchone()['id']
        db.execute("INSERT INTO joke (title, body, author_id) VALUES (?, ?, ?)",
                   ('Another Joke', 'Haha', other_user_id))
        db.commit()
        joke_id = db.execute("SELECT id FROM joke WHERE title = ?", 
                             ('Another Joke',)).fetchone()['id']

    client.post('/joke/take', data={'joke_id': joke_id}, follow_redirects=True)
    rv = client.post('/joke/take', data={'joke_id': joke_id}, follow_redirects=True)

    assert b'You have already taken this joke!' in rv.data


def test_unsuccessful_take_joke(client):
    login(client)
    
    with client.application.app_context():
        db = get_db()        
        db.execute("INSERT INTO user (email, nickname, password) VALUES (?, ?, ?)",
                   ('other@example.com', 'otherguy', 'pass'))
        other_user_id = db.execute("SELECT id FROM user WHERE email = ?", 
                                   ('other@example.com',)).fetchone()['id']
        db.execute("INSERT INTO joke (title, body, author_id) VALUES (?, ?, ?)",
                   ('Another Joke', 'Haha', other_user_id))
        db.commit()
        joke_id = db.execute("SELECT id FROM joke WHERE title = ?", 
                             ('Another Joke',)).fetchone()['id']

    rv = client.post('/joke/take', data={'joke_id': joke_id}, follow_redirects=True)

    assert b'You need to leave a joke first!' in rv.data


def test_view_joke(client):
    login(client)
    client.post('/joke/leave', data={
        'title': 'Unique Title',
          'body': 'A punchline'
    })
    rv = client.get('/joke/my')
    print(rv.data)
    assert b'Unique Title' in rv.data

def test_view_no_joke(client):
    login(client)
    rv = client.get('/joke/my')
    print(rv.data)
    assert b'No jokes found' in rv.data



def test_not_enough_joke_balance_to_view(client):
    login(client)

    with client.application.app_context():
        db = get_db()
        db.execute("INSERT INTO user (email, nickname, password) VALUES (?, ?, ?)",
                   ('other@example.com', 'otherguy', 'pass'))
        other_user_id = db.execute("SELECT id FROM user WHERE email = ?",
                                   ('other@example.com',)).fetchone()['id']
        db.execute("INSERT INTO joke (title, body, author_id) VALUES (?, ?, ?)",
                   ('View Joke', 'Hilarious', other_user_id))
        db.execute("UPDATE user SET joke_balance = 0 WHERE email = ?", ('test@example.com',))
        db.commit()
        joke_id = db.execute("SELECT id FROM joke WHERE title = ?", ('View Joke',)).fetchone()['id']

    rv = client.get(f'/joke/view/{joke_id}', follow_redirects=True)
    assert b'Not enough joke balance to view this joke!' in rv.data


def test_rating_submission(client):
    login(client)

    client.post('/joke/leave', data={
        'title': 'Rating Test',
        'body': 'Very funny'
    })

    with client.application.app_context():
        db = get_db()
        db.execute("INSERT INTO user (email, nickname, password) VALUES (?, ?, ?)",
                   ('ratejoke@example.com', 'ratethejokeguy', 'pass'))
        other_user_id = db.execute("SELECT id FROM user WHERE email = ?", 
                                   ('ratejoke@example.com',)).fetchone()['id']
        db.execute("INSERT INTO joke (title, body, author_id) VALUES (?, ?, ?)",
                   ('Another Joke to Rate', 'Haha Hoho', other_user_id))
        db.commit()
        joke_id = db.execute("SELECT id FROM joke WHERE title = ?", 
                             ('Another Joke to Rate',)).fetchone()['id']                

    rv = client.post(f'/joke/view/{joke_id}', data={'action': 'rate', 'rating': 4}, follow_redirects=True)
    assert b'Your rating has been submitted!' in rv.data


def test_rating_update(client):
    login(client)

    client.post('/joke/leave', data={
        'title': 'Rating Update Test',
        'body': 'Still funny'
    })

    with client.application.app_context():
        db = get_db()
        db.execute("INSERT INTO user (email, nickname, password) VALUES (?, ?, ?)",
                   ('ratejoke@example.com', 'ratethejokeguy', 'pass'))
        other_user_id = db.execute("SELECT id FROM user WHERE email = ?", 
                                   ('ratejoke@example.com',)).fetchone()['id']
        db.execute("INSERT INTO joke (title, body, author_id) VALUES (?, ?, ?)",
                   ('Another Joke to Rate', 'Haha Hoho', other_user_id))
        db.commit()
        joke_id = db.execute("SELECT id FROM joke WHERE title = ?", 
                             ('Another Joke to Rate',)).fetchone()['id']
        

    client.post(f'/joke/view/{joke_id}', data={'action': 'rate', 'rating': 2}, follow_redirects=True)
    rv = client.post(f'/joke/view/{joke_id}', data={'action': 'rate', 'rating': 5}, follow_redirects=True)
    assert b'Your rating has been updated!' in rv.data


def test_joke_delete(client):
    login(client)

    client.post('/joke/leave', data={
        'title': 'Delete Me',
        'body': 'To be deleted'
    })

    with client.application.app_context():
        db = get_db()
        joke_id = db.execute("SELECT id FROM joke WHERE title = ?", ('Delete Me',)).fetchone()['id']

    rv = client.post(f'/joke/view/{joke_id}', data={'action': 'delete'}, follow_redirects=True)
    assert b'Joke deleted.' in rv.data


def test_joke_update(client):
    login(client)

    client.post('/joke/leave', data={
        'title': 'Update Me',
        'body': 'Old version'
    })

    with client.application.app_context():
        db = get_db()
        joke_id = db.execute("SELECT id FROM joke WHERE title = ?", ('Update Me',)).fetchone()['id']

    rv = client.post(f'/joke/view/{joke_id}', data={'action': 'update', 'body': 'Updated version'}, follow_redirects=True)
    assert b'Joke updated successfully!' in rv.data
