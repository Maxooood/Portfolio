from app.models.user import UserRole
from tests.conftest import make_user, make_equipment, make_fault_type, get_token


def auth_headers(token):
    return {'Authorization': f'Bearer {token}'}


class TestEquipmentAPI:
    def test_list_equipment_authenticated(self, client, db):
        user = make_user(db, role=UserRole.SHIFT_MANAGER, suffix='300')
        token = get_token(client, user.email)
        resp = client.get('/api/equipment', headers=auth_headers(token))
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_list_equipment_unauthenticated(self, client, db):
        resp = client.get('/api/equipment')
        assert resp.status_code == 401

    def test_dispatcher_can_create_equipment(self, client, db):
        user = make_user(db, role=UserRole.DISPATCHER, suffix='301')
        token = get_token(client, user.email)

        resp = client.post('/api/equipment', headers=auth_headers(token), json={
            'name': 'Компрессор К-100',
            'inventory_number': 'INV-K-100',
            'equipment_type': 'Компрессор',
            'location': 'Цех-2',
            'department': 'Производство',
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['inventory_number'] == 'INV-K-100'

    def test_executor_cannot_create_equipment(self, client, db):
        user = make_user(db, role=UserRole.EXECUTOR, suffix='302')
        token = get_token(client, user.email)
        resp = client.post('/api/equipment', headers=auth_headers(token), json={
            'name': 'Test', 'inventory_number': 'INV-EXEC-001',
        })
        assert resp.status_code == 403

    def test_duplicate_inventory_number(self, client, db):
        make_equipment(db, 'INV-DUP-001')
        user = make_user(db, role=UserRole.DISPATCHER, suffix='303')
        token = get_token(client, user.email)

        resp = client.post('/api/equipment', headers=auth_headers(token), json={
            'name': 'Duplicate', 'inventory_number': 'INV-DUP-001',
        })
        assert resp.status_code == 409


class TestFaultTypeAPI:
    def test_list_fault_types(self, client, db):
        make_fault_type(db, 'Электрика-T')
        user = make_user(db, role=UserRole.SHIFT_MANAGER, suffix='310')
        token = get_token(client, user.email)

        resp = client.get('/api/fault-types', headers=auth_headers(token))
        assert resp.status_code == 200
        items = resp.get_json()
        assert any(ft['name'] == 'Электрика-T' for ft in items)

    def test_admin_can_create_fault_type(self, client, db):
        user = make_user(db, role=UserRole.ADMIN, suffix='311')
        token = get_token(client, user.email)

        resp = client.post('/api/fault-types', headers=auth_headers(token), json={
            'name': 'Механика-New',
            'description': 'Механические неисправности',
        })
        assert resp.status_code == 201

    def test_non_admin_cannot_create_fault_type(self, client, db):
        user = make_user(db, role=UserRole.DISPATCHER, suffix='312')
        token = get_token(client, user.email)

        resp = client.post('/api/fault-types', headers=auth_headers(token), json={
            'name': 'Unauthorized',
        })
        assert resp.status_code == 403
