import pytest
from app import create_app
from database import db, User

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_user_registration(client, app):
    # 1. Success Registration
    response = client.post('/register', data={
        'username': 'testcoder',
        'email': 'coder@example.com',
        'password': 'secretpassword',
        'confirm_password': 'secretpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Registration successful" in response.data

    # Check database presence
    with app.app_context():
        user = User.query.filter_by(username='testcoder').first()
        assert user is not None
        assert user.email == 'coder@example.com'
        assert user.check_password('secretpassword') is True

    # 2. Duplicate Registration Checks
    response2 = client.post('/register', data={
        'username': 'testcoder',
        'email': 'different@example.com',
        'password': 'secretpassword',
        'confirm_password': 'secretpassword'
    }, follow_redirects=True)
    assert b"Username is already taken" in response2.data


def test_user_login_logout(client):
    # Register first
    client.post('/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })

    # 1. Attempt login with wrong password
    response_wrong = client.post('/login', data={
        'username_or_email': 'testuser',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert b"Invalid username/email or password" in response_wrong.data

    # 2. Correct credentials login
    response_ok = client.post('/login', data={
        'username_or_email': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)
    assert b"Welcome back, testuser!" in response_ok.data

    # 3. Logout
    response_out = client.get('/logout', follow_redirects=True)
    assert b"You have been logged out" in response_out.data
