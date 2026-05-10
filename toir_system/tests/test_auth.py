import pytest
from app.models.user import UserRole
from tests.conftest import make_user, get_token


class TestLogin:
    def test_login_success(self, client, db):
        user = make_user(db, role=UserRole.SHIFT_MANAGER, suffix='100')
        resp = client.post('/api/auth/login', json={
            'email': user.email,
            'password': 'password123',
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'access_token' in data
        assert data['user']['email'] == user.email
        assert data['user']['role'] == UserRole.SHIFT_MANAGER

    def test_login_wrong_password(self, client, db):
        user = make_user(db, suffix='101')
        resp = client.post('/api/auth/login', json={
            'email': user.email,
            'password': 'wrongpassword',
        })
        assert resp.status_code == 401

    def test_login_unknown_email(self, client, db):
        resp = client.post('/api/auth/login', json={
            'email': 'nobody@test.com',
            'password': 'password123',
        })
        assert resp.status_code == 401

    def test_login_missing_fields(self, client, db):
        resp = client.post('/api/auth/login', json={'email': 'test@test.com'})
        assert resp.status_code == 400

    def test_login_inactive_user(self, client, db):
        user = make_user(db, suffix='102')
        user.is_active = False
        db.session.commit()
        resp = client.post('/api/auth/login', json={
            'email': user.email,
            'password': 'password123',
        })
        assert resp.status_code == 403


class TestGetMe:
    def test_get_me_authenticated(self, client, db):
        user = make_user(db, suffix='103')
        token = get_token(client, user.email)
        resp = client.get('/api/auth/me', headers={'Authorization': f'Bearer {token}'})
        assert resp.status_code == 200
        assert resp.get_json()['id'] == user.id

    def test_get_me_no_token(self, client, db):
        resp = client.get('/api/auth/me')
        assert resp.status_code == 401


class TestLogout:
    def test_logout(self, client, db):
        user = make_user(db, suffix='104')
        token = get_token(client, user.email)
        resp = client.post('/api/auth/logout', headers={'Authorization': f'Bearer {token}'})
        assert resp.status_code == 200
