from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.api import api_bp
from app.extensions import db
from app.models.equipment import Equipment, FaultType
from app.models.user import UserRole
from app.utils.decorators import roles_required, get_current_user
from app.utils.helpers import log_audit


@api_bp.route('/equipment', methods=['GET'])
@jwt_required()
def list_equipment():
    query = Equipment.query
    department = request.args.get('department')
    status = request.args.get('status')
    if department:
        query = query.filter_by(department=department)
    if status:
        query = query.filter_by(status=status)
    items = query.order_by(Equipment.name).all()
    return jsonify([e.to_dict() for e in items]), 200


@api_bp.route('/equipment/<int:eq_id>', methods=['GET'])
@jwt_required()
def get_equipment(eq_id):
    eq = Equipment.query.get_or_404(eq_id)
    return jsonify(eq.to_dict()), 200


@api_bp.route('/equipment', methods=['POST'])
@roles_required(UserRole.DISPATCHER, UserRole.ADMIN)
def create_equipment():
    user = get_current_user()
    data = request.get_json()
    for field in ['name', 'inventory_number']:
        if not data.get(field):
            return jsonify({'error': f'Поле {field} обязательно'}), 400

    if Equipment.query.filter_by(inventory_number=data['inventory_number']).first():
        return jsonify({'error': 'Оборудование с таким инвентарным номером уже существует'}), 409

    eq = Equipment(
        name=data['name'],
        inventory_number=data['inventory_number'],
        equipment_type=data.get('equipment_type'),
        location=data.get('location'),
        department=data.get('department'),
        manufacturer=data.get('manufacturer'),
        model=data.get('model'),
        year_of_manufacture=data.get('year_of_manufacture'),
    )
    db.session.add(eq)
    log_audit(user.id, 'EQUIPMENT_CREATED', 'equipment', None,
              details=data['inventory_number'], ip_address=request.remote_addr)
    db.session.commit()
    current_app.logger.info(f'Equipment {data["inventory_number"]} created')
    return jsonify(eq.to_dict()), 201


@api_bp.route('/equipment/<int:eq_id>', methods=['PUT'])
@roles_required(UserRole.DISPATCHER, UserRole.ADMIN)
def update_equipment(eq_id):
    user = get_current_user()
    eq = Equipment.query.get_or_404(eq_id)
    data = request.get_json()
    for field in ['name', 'equipment_type', 'location', 'department', 'manufacturer', 'model',
                  'year_of_manufacture', 'status']:
        if field in data:
            setattr(eq, field, data[field])
    log_audit(user.id, 'EQUIPMENT_UPDATED', 'equipment', eq.id, ip_address=request.remote_addr)
    db.session.commit()
    return jsonify(eq.to_dict()), 200


@api_bp.route('/fault-types', methods=['GET'])
@jwt_required()
def list_fault_types():
    items = FaultType.query.filter_by(is_active=True).order_by(FaultType.name).all()
    return jsonify([f.to_dict() for f in items]), 200


@api_bp.route('/fault-types', methods=['POST'])
@roles_required(UserRole.ADMIN)
def create_fault_type():
    user = get_current_user()
    data = request.get_json()
    if not data.get('name'):
        return jsonify({'error': 'Поле name обязательно'}), 400
    if FaultType.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Тип неисправности с таким названием уже существует'}), 409
    ft = FaultType(name=data['name'], description=data.get('description'))
    db.session.add(ft)
    log_audit(user.id, 'FAULT_TYPE_CREATED', 'fault_type', None,
              details=data['name'], ip_address=request.remote_addr)
    db.session.commit()
    return jsonify(ft.to_dict()), 201
