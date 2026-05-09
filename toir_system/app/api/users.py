from flask import request, jsonify, current_app
from app.api import api_bp
from app.extensions import db
from app.models.user import User, UserRole
from app.utils.decorators import roles_required, get_current_user
from app.utils.helpers import log_audit


@api_bp.route('/users', methods=['GET'])
@roles_required(UserRole.ADMIN, UserRole.MANAGER)
def list_users():
    role_filter = request.args.get('role')
    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)
    users = query.order_by(User.full_name).all()
    return jsonify([u.to_dict() for u in users]), 200


@api_bp.route('/users/<int:user_id>', methods=['GET'])
@roles_required(UserRole.ADMIN, UserRole.MANAGER)
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


@api_bp.route('/users', methods=['POST'])
@roles_required(UserRole.ADMIN)
def create_user():
    current_user = get_current_user()
    data = request.get_json()
    required = ['employee_number', 'full_name', 'email', 'password', 'role']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Поле {field} обязательно'}), 400
    if data['role'] not in UserRole.ALL:
        return jsonify({'error': f'Недопустимая роль. Доступные роли: {UserRole.ALL}'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Пользователь с таким email уже существует'}), 409
    if User.query.filter_by(employee_number=data['employee_number']).first():
        return jsonify({'error': 'Пользователь с таким табельным номером уже существует'}), 409

    user = User(
        employee_number=data['employee_number'],
        full_name=data['full_name'],
        email=data['email'].lower(),
        role=data['role'],
        department=data.get('department'),
        phone=data.get('phone'),
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.flush()
    log_audit(current_user.id, 'USER_CREATED', 'user', user.id,
              details=data['employee_number'], ip_address=request.remote_addr)
    db.session.commit()
    current_app.logger.info(f'User {data["employee_number"]} created by admin {current_user.employee_number}')
    return jsonify(user.to_dict()), 201


@api_bp.route('/users/<int:user_id>', methods=['PUT'])
@roles_required(UserRole.ADMIN)
def update_user(user_id):
    current_user = get_current_user()
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    for field in ['full_name', 'department', 'phone', 'is_active']:
        if field in data:
            setattr(user, field, data[field])
    if 'role' in data:
        if data['role'] not in UserRole.ALL:
            return jsonify({'error': 'Недопустимая роль'}), 400
        user.role = data['role']
    if 'password' in data and data['password']:
        user.set_password(data['password'])

    log_audit(current_user.id, 'USER_UPDATED', 'user', user.id, ip_address=request.remote_addr)
    db.session.commit()
    current_app.logger.info(f'User {user.employee_number} updated by admin')
    return jsonify(user.to_dict()), 200
