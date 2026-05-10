from datetime import datetime, timezone
from flask import request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.api import api_bp
from app.extensions import db
from app.models.user import User
from app.utils.helpers import log_audit


@api_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Данные не переданы'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email и пароль обязательны'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        current_app.logger.warning(f'Failed login attempt for email={email}')
        return jsonify({'error': 'Неверный email или пароль'}), 401

    if not user.is_active:
        return jsonify({'error': 'Аккаунт деактивирован'}), 403

    user.last_login = datetime.now(timezone.utc)
    log_audit(user.id, 'USER_LOGIN', 'user', user.id, ip_address=request.remote_addr)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    current_app.logger.info(f'User {user.employee_number} logged in successfully')
    return jsonify({'access_token': token, 'user': user.to_dict()}), 200


@api_bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Пользователь не найден'}), 404
    return jsonify(user.to_dict()), 200


@api_bp.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    user_id = int(get_jwt_identity())
    log_audit(user_id, 'USER_LOGOUT', 'user', user_id, ip_address=request.remote_addr)
    db.session.commit()
    current_app.logger.info(f'User {user_id} logged out')
    return jsonify({'message': 'Выход выполнен успешно'}), 200
