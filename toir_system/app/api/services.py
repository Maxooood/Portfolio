from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.api import api_bp
from app.extensions import db
from app.models.service import AuxiliaryService, RoutingRule
from app.models.user import UserRole
from app.utils.decorators import roles_required, get_current_user
from app.utils.helpers import log_audit


@api_bp.route('/services', methods=['GET'])
@jwt_required()
def list_services():
    items = AuxiliaryService.query.filter_by(is_active=True).order_by(AuxiliaryService.name).all()
    return jsonify([s.to_dict() for s in items]), 200


@api_bp.route('/services', methods=['POST'])
@roles_required(UserRole.ADMIN)
def create_service():
    user = get_current_user()
    data = request.get_json()
    for field in ['code', 'name']:
        if not data.get(field):
            return jsonify({'error': f'Поле {field} обязательно'}), 400
    if AuxiliaryService.query.filter_by(code=data['code']).first():
        return jsonify({'error': 'Служба с таким кодом уже существует'}), 409
    svc = AuxiliaryService(
        code=data['code'],
        name=data['name'],
        specialization=data.get('specialization'),
        contact_person=data.get('contact_person'),
        contact_phone=data.get('contact_phone'),
    )
    db.session.add(svc)
    log_audit(user.id, 'SERVICE_CREATED', 'service', None,
              details=data['code'], ip_address=request.remote_addr)
    db.session.commit()
    current_app.logger.info(f'Service {data["code"]} created')
    return jsonify(svc.to_dict()), 201


@api_bp.route('/services/<int:svc_id>', methods=['PUT'])
@roles_required(UserRole.ADMIN)
def update_service(svc_id):
    user = get_current_user()
    svc = AuxiliaryService.query.get_or_404(svc_id)
    data = request.get_json()
    for field in ['name', 'specialization', 'contact_person', 'contact_phone', 'is_active']:
        if field in data:
            setattr(svc, field, data[field])
    log_audit(user.id, 'SERVICE_UPDATED', 'service', svc.id, ip_address=request.remote_addr)
    db.session.commit()
    return jsonify(svc.to_dict()), 200


@api_bp.route('/routing-rules', methods=['GET'])
@roles_required(UserRole.DISPATCHER, UserRole.ADMIN)
def list_routing_rules():
    items = RoutingRule.query.order_by(RoutingRule.priority).all()
    return jsonify([r.to_dict() for r in items]), 200


@api_bp.route('/routing-rules', methods=['POST'])
@roles_required(UserRole.ADMIN)
def create_routing_rule():
    user = get_current_user()
    data = request.get_json()
    for field in ['fault_type_id', 'service_id']:
        if not data.get(field):
            return jsonify({'error': f'Поле {field} обязательно'}), 400
    rule = RoutingRule(
        fault_type_id=data['fault_type_id'],
        service_id=data['service_id'],
        priority=data.get('priority', 1),
    )
    db.session.add(rule)
    log_audit(user.id, 'ROUTING_RULE_CREATED', 'routing_rule', None, ip_address=request.remote_addr)
    db.session.commit()
    current_app.logger.info(f'Routing rule created: fault_type={data["fault_type_id"]} -> service={data["service_id"]}')
    return jsonify(rule.to_dict()), 201


@api_bp.route('/routing-rules/<int:rule_id>', methods=['PUT'])
@roles_required(UserRole.ADMIN)
def update_routing_rule(rule_id):
    user = get_current_user()
    rule = RoutingRule.query.get_or_404(rule_id)
    data = request.get_json()
    for field in ['fault_type_id', 'service_id', 'priority', 'is_active']:
        if field in data:
            setattr(rule, field, data[field])
    log_audit(user.id, 'ROUTING_RULE_UPDATED', 'routing_rule', rule.id, ip_address=request.remote_addr)
    db.session.commit()
    return jsonify(rule.to_dict()), 200


@api_bp.route('/routing-rules/<int:rule_id>', methods=['DELETE'])
@roles_required(UserRole.ADMIN)
def delete_routing_rule(rule_id):
    user = get_current_user()
    rule = RoutingRule.query.get_or_404(rule_id)
    db.session.delete(rule)
    log_audit(user.id, 'ROUTING_RULE_DELETED', 'routing_rule', rule_id, ip_address=request.remote_addr)
    db.session.commit()
    return jsonify({'message': 'Правило удалено'}), 200
