import pytest
from app import create_app
from app.extensions import db as _db
from app.models.user import User, UserRole
from app.models.equipment import Equipment, FaultType
from app.models.service import AuxiliaryService, RoutingRule


@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    with app.app_context():
        yield _db
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture
def client(app):
    return app.test_client()


def make_user(db, role=UserRole.SHIFT_MANAGER, suffix='001'):
    user = User(
        employee_number=f'EMP-{suffix}',
        full_name=f'Test User {suffix}',
        email=f'user{suffix}@test.com',
        role=role,
        department='Test Dept',
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user


def make_equipment(db, inventory_number='INV-001'):
    eq = Equipment(
        name='Test Pump',
        inventory_number=inventory_number,
        equipment_type='Насос',
        location='Цех-1',
        department='Производство',
    )
    db.session.add(eq)
    db.session.commit()
    return eq


def make_fault_type(db, name='Электрическая неисправность'):
    ft = FaultType(name=name, description='Test fault type')
    db.session.add(ft)
    db.session.commit()
    return ft


def make_service(db, code='ELEC'):
    svc = AuxiliaryService(
        code=code,
        name='Электромонтёры',
        specialization='Электрика',
    )
    db.session.add(svc)
    db.session.commit()
    return svc


def get_token(client, email, password='password123'):
    resp = client.post('/api/auth/login', json={'email': email, 'password': password})
    return resp.get_json()['access_token']
