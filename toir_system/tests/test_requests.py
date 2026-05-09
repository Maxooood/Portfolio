import pytest
from app.models.user import UserRole
from app.models.request import RequestStatus
from tests.conftest import make_user, make_equipment, make_fault_type, make_service, get_token


def auth_headers(token):
    return {'Authorization': f'Bearer {token}'}


class TestCreateRequest:
    def test_shift_manager_can_create(self, client, db):
        user = make_user(db, role=UserRole.SHIFT_MANAGER, suffix='200')
        eq = make_equipment(db, 'INV-200')
        token = get_token(client, user.email)

        resp = client.post('/api/requests', headers=auth_headers(token), json={
            'title': 'Насос не работает',
            'description': 'Насос П-101 перестал качать',
            'equipment_id': eq.id,
            'priority': 'high',
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['status'] == RequestStatus.NEW
        assert data['initiator_id'] == user.id
        assert data['equipment_id'] == eq.id
        assert data['request_number'].startswith('REQ-')

    def test_executor_cannot_create(self, client, db):
        user = make_user(db, role=UserRole.EXECUTOR, suffix='201')
        eq = make_equipment(db, 'INV-201')
        token = get_token(client, user.email)

        resp = client.post('/api/requests', headers=auth_headers(token), json={
            'title': 'Test',
            'description': 'Test desc',
            'equipment_id': eq.id,
        })
        assert resp.status_code == 403

    def test_missing_required_fields(self, client, db):
        user = make_user(db, role=UserRole.SHIFT_MANAGER, suffix='202')
        token = get_token(client, user.email)

        resp = client.post('/api/requests', headers=auth_headers(token), json={
            'title': 'Test',
        })
        assert resp.status_code == 400

    def test_auto_routing_on_create(self, client, db):
        user = make_user(db, role=UserRole.SHIFT_MANAGER, suffix='203')
        eq = make_equipment(db, 'INV-203')
        ft = make_fault_type(db, 'Электрика-Test')
        svc = make_service(db, 'ELEC-203')
        from app.models.service import RoutingRule
        rule = RoutingRule(fault_type_id=ft.id, service_id=svc.id, priority=1)
        db.session.add(rule)
        db.session.commit()

        token = get_token(client, user.email)
        resp = client.post('/api/requests', headers=auth_headers(token), json={
            'title': 'Электрическая проблема',
            'description': 'Нет питания',
            'equipment_id': eq.id,
            'fault_type_id': ft.id,
        })
        assert resp.status_code == 201
        assert resp.get_json()['service_id'] == svc.id


class TestGetRequests:
    def test_list_requests(self, client, db):
        user = make_user(db, role=UserRole.DISPATCHER, suffix='210')
        token = get_token(client, user.email)
        resp = client.get('/api/requests', headers=auth_headers(token))
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'items' in data
        assert 'total' in data

    def test_get_single_request(self, client, db):
        manager = make_user(db, role=UserRole.SHIFT_MANAGER, suffix='211')
        eq = make_equipment(db, 'INV-211')
        token = get_token(client, manager.email)

        create_resp = client.post('/api/requests', headers=auth_headers(token), json={
            'title': 'Single test',
            'description': 'Desc',
            'equipment_id': eq.id,
        })
        req_id = create_resp.get_json()['id']

        resp = client.get(f'/api/requests/{req_id}', headers=auth_headers(token))
        assert resp.status_code == 200
        assert resp.get_json()['id'] == req_id

    def test_get_nonexistent_request(self, client, db):
        user = make_user(db, role=UserRole.DISPATCHER, suffix='212')
        token = get_token(client, user.email)
        resp = client.get('/api/requests/99999', headers=auth_headers(token))
        assert resp.status_code == 404


class TestStatusTransitions:
    def _create_request(self, client, db, suffix):
        manager = make_user(db, role=UserRole.SHIFT_MANAGER, suffix=suffix)
        eq = make_equipment(db, f'INV-{suffix}')
        token = get_token(client, manager.email)
        resp = client.post('/api/requests', headers=auth_headers(token), json={
            'title': 'Status test',
            'description': 'Test',
            'equipment_id': eq.id,
        })
        return resp.get_json()['id'], manager

    def test_dispatcher_can_assign(self, client, db):
        req_id, _ = self._create_request(client, db, '220')
        dispatcher = make_user(db, role=UserRole.DISPATCHER, suffix='221')
        executor = make_user(db, role=UserRole.EXECUTOR, suffix='222')
        token = get_token(client, dispatcher.email)

        resp = client.put(f'/api/requests/{req_id}/status', headers=auth_headers(token), json={
            'status': RequestStatus.ASSIGNED,
            'executor_id': executor.id,
        })
        assert resp.status_code == 200
        assert resp.get_json()['status'] == RequestStatus.ASSIGNED

    def test_invalid_transition(self, client, db):
        req_id, manager = self._create_request(client, db, '223')
        token = get_token(client, manager.email)
        resp = client.put(f'/api/requests/{req_id}/status', headers=auth_headers(token), json={
            'status': RequestStatus.CLOSED,
        })
        assert resp.status_code == 400

    def test_shift_manager_cannot_assign(self, client, db):
        req_id, manager = self._create_request(client, db, '224')
        token = get_token(client, manager.email)
        resp = client.put(f'/api/requests/{req_id}/status', headers=auth_headers(token), json={
            'status': RequestStatus.ASSIGNED,
        })
        assert resp.status_code == 403

    def test_full_lifecycle(self, client, db):
        req_id, _ = self._create_request(client, db, '230')
        dispatcher = make_user(db, role=UserRole.DISPATCHER, suffix='231')
        executor = make_user(db, role=UserRole.EXECUTOR, suffix='232')
        d_token = get_token(client, dispatcher.email)
        e_token = get_token(client, executor.email)

        # Assign
        client.put(f'/api/requests/{req_id}/status', headers=auth_headers(d_token), json={
            'status': RequestStatus.ASSIGNED, 'executor_id': executor.id,
        })
        # In progress
        client.put(f'/api/requests/{req_id}/status', headers=auth_headers(e_token), json={
            'status': RequestStatus.IN_PROGRESS,
        })
        # Diagnostic
        diag_resp = client.post(f'/api/requests/{req_id}/diagnostic', headers=auth_headers(e_token), json={
            'cause': 'Сгорела обмотка ротора',
            'repair_required': True,
        })
        assert diag_resp.status_code == 201

        # Repair
        repair_resp = client.post(f'/api/requests/{req_id}/repair', headers=auth_headers(e_token), json={
            'operations': 'Замена обмотки ротора',
            'labor_hours': 4.5,
            'completed': True,
            'materials': [{'name': 'Обмотка', 'quantity': 1, 'unit': 'шт', 'cost': 5000.0}],
        })
        assert repair_resp.status_code == 201

        # Close
        close_resp = client.put(f'/api/requests/{req_id}/status', headers=auth_headers(d_token), json={
            'status': RequestStatus.CLOSED,
        })
        assert close_resp.status_code == 200

        final = client.get(f'/api/requests/{req_id}', headers=auth_headers(d_token)).get_json()
        assert final['status'] == RequestStatus.CLOSED
        assert final['diagnostic'] is not None
        assert final['repair'] is not None
        assert len(final['status_history']) > 0
