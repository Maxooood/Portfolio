import pytest
from app.models.user import User, UserRole
from app.models.request import RequestStatus
from app.models.equipment import Equipment


class TestUser:
    def test_password_hashing(self, app, db):
        with app.app_context():
            user = User(
                employee_number='TEST-001',
                full_name='Иванов Иван Иванович',
                email='ivanov@test.com',
                role=UserRole.SHIFT_MANAGER,
            )
            user.set_password('securepassword')
            db.session.add(user)
            db.session.commit()

            assert user.check_password('securepassword') is True
            assert user.check_password('wrongpassword') is False
            assert 'securepassword' not in user.password_hash

    def test_user_to_dict(self, app, db):
        with app.app_context():
            user = User(
                employee_number='TEST-002',
                full_name='Петров Петр Петрович',
                email='petrov@test.com',
                role=UserRole.DISPATCHER,
            )
            user.set_password('pass')
            db.session.add(user)
            db.session.commit()

            d = user.to_dict()
            assert d['employee_number'] == 'TEST-002'
            assert d['role'] == UserRole.DISPATCHER
            assert 'password_hash' not in d

    def test_all_roles_defined(self):
        assert UserRole.SHIFT_MANAGER in UserRole.ALL
        assert UserRole.EXECUTOR in UserRole.ALL
        assert UserRole.DISPATCHER in UserRole.ALL
        assert UserRole.MANAGER in UserRole.ALL
        assert UserRole.ADMIN in UserRole.ALL


class TestRequestStatusMachine:
    def test_allowed_transitions(self):
        assert RequestStatus.can_transition(RequestStatus.NEW, RequestStatus.ASSIGNED) is True
        assert RequestStatus.can_transition(RequestStatus.ASSIGNED, RequestStatus.IN_PROGRESS) is True
        assert RequestStatus.can_transition(RequestStatus.IN_PROGRESS, RequestStatus.DIAGNOSTICS_DONE) is True
        assert RequestStatus.can_transition(RequestStatus.DIAGNOSTICS_DONE, RequestStatus.REPAIR_IN_PROGRESS) is True
        assert RequestStatus.can_transition(RequestStatus.COMPLETED, RequestStatus.CLOSED) is True

    def test_forbidden_transitions(self):
        assert RequestStatus.can_transition(RequestStatus.NEW, RequestStatus.CLOSED) is False
        assert RequestStatus.can_transition(RequestStatus.NEW, RequestStatus.COMPLETED) is False
        assert RequestStatus.can_transition(RequestStatus.CLOSED, RequestStatus.NEW) is False
        assert RequestStatus.can_transition(RequestStatus.CLOSED, RequestStatus.IN_PROGRESS) is False

    def test_cancellation_allowed(self):
        assert RequestStatus.can_transition(RequestStatus.NEW, RequestStatus.CANCELLED) is True
        assert RequestStatus.can_transition(RequestStatus.ASSIGNED, RequestStatus.CANCELLED) is True

    def test_cancelled_is_terminal(self):
        for status in RequestStatus.ALL:
            assert RequestStatus.can_transition(RequestStatus.CANCELLED, status) is False


class TestEquipment:
    def test_equipment_to_dict(self, app, db):
        with app.app_context():
            eq = Equipment(
                name='Центробежный насос ЦНС-60',
                inventory_number='INV-MODEL-001',
                equipment_type='Насос',
                location='Цех-3',
                department='НПЗ',
            )
            db.session.add(eq)
            db.session.commit()

            d = eq.to_dict()
            assert d['name'] == 'Центробежный насос ЦНС-60'
            assert d['inventory_number'] == 'INV-MODEL-001'
            assert d['status'] == 'operational'
