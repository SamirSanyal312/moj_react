def test_login_required_redirect(client):
    rv = client.get('/joke/', follow_redirects=True)
    assert b'Login' in rv.data

def test_leave_without_login(client):
    rv = client.post('/joke/leave', data={'title': 'Oops', 'body': 'no access'}, follow_redirects=True)
    assert b'Login' in rv.data
