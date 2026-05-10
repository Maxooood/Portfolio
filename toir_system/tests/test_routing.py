import pytest
from app.models.service import RoutingRule
from app.services.routing import route_request
from tests.conftest import make_fault_type, make_service


class TestRoutingService:
    def test_route_with_active_rule(self, app, db):
        with app.app_context():
            ft = make_fault_type(db, 'Механика-R')
            svc = make_service(db, 'MECH-R')
            rule = RoutingRule(fault_type_id=ft.id, service_id=svc.id, priority=1, is_active=True)
            db.session.add(rule)
            db.session.commit()

            result = route_request(ft.id)
            assert result == svc.id

    def test_route_with_no_fault_type(self, app, db):
        with app.app_context():
            result = route_request(None)
            assert result is None

    def test_route_with_no_rule(self, app, db):
        with app.app_context():
            ft = make_fault_type(db, 'NoRule-R')
            db.session.commit()
            result = route_request(ft.id)
            assert result is None

    def test_route_selects_highest_priority(self, app, db):
        with app.app_context():
            ft = make_fault_type(db, 'Priority-R')
            svc1 = make_service(db, 'SVC1-R')
            svc2 = make_service(db, 'SVC2-R')
            rule1 = RoutingRule(fault_type_id=ft.id, service_id=svc1.id, priority=2, is_active=True)
            rule2 = RoutingRule(fault_type_id=ft.id, service_id=svc2.id, priority=1, is_active=True)
            db.session.add_all([rule1, rule2])
            db.session.commit()

            result = route_request(ft.id)
            assert result == svc2.id  # priority=1 wins (lower number = higher priority)

    def test_inactive_rule_ignored(self, app, db):
        with app.app_context():
            ft = make_fault_type(db, 'Inactive-R')
            svc = make_service(db, 'INACT-R')
            rule = RoutingRule(fault_type_id=ft.id, service_id=svc.id, priority=1, is_active=False)
            db.session.add(rule)
            db.session.commit()

            result = route_request(ft.id)
            assert result is None
