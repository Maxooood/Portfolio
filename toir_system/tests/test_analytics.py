from app.models.user import UserRole
from tests.conftest import make_user, get_token


def auth_headers(token):
    return {'Authorization': f'Bearer {token}'}


class TestAnalyticsAPI:
    def test_manager_can_access_summary(self, client, db):
        user = make_user(db, role=UserRole.MANAGER, suffix='400')
        token = get_token(client, user.email)
        resp = client.get('/api/analytics/summary', headers=auth_headers(token))
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'total_requests' in data
        assert 'by_status' in data
        assert 'avg_resolution_hours' in data

    def test_executor_cannot_access_summary(self, client, db):
        user = make_user(db, role=UserRole.EXECUTOR, suffix='401')
        token = get_token(client, user.email)
        resp = client.get('/api/analytics/summary', headers=auth_headers(token))
        assert resp.status_code == 403

    def test_equipment_faults_stats(self, client, db):
        user = make_user(db, role=UserRole.MANAGER, suffix='402')
        token = get_token(client, user.email)
        resp = client.get('/api/analytics/equipment-faults', headers=auth_headers(token))
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_service_performance(self, client, db):
        user = make_user(db, role=UserRole.MANAGER, suffix='403')
        token = get_token(client, user.email)
        resp = client.get('/api/analytics/service-performance', headers=auth_headers(token))
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_summary_with_date_filter(self, client, db):
        user = make_user(db, role=UserRole.MANAGER, suffix='404')
        token = get_token(client, user.email)
        resp = client.get(
            '/api/analytics/summary?date_from=2025-01-01&date_to=2025-12-31',
            headers=auth_headers(token),
        )
        assert resp.status_code == 200
