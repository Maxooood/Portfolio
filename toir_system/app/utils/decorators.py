import functools
from flask import jsonify, current_app
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.user import User


def roles_required(*roles):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = int(get_jwt_identity())
            user = User.query.get(user_id)
            if not user or not user.is_active:
                current_app.logger.warning(f'Access denied: user {user_id} not found or inactive')
                return jsonify({'error': 'Пользователь не найден или деактивирован'}), 403
            if user.role not in roles:
                current_app.logger.warning(
                    f'Access denied: user {user_id} (role={user.role}) tried to access endpoint requiring {roles}'
                )
                return jsonify({'error': 'Недостаточно прав доступа'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def get_current_user() -> User | None:
    user_id = int(get_jwt_identity())
    return User.query.get(user_id) if user_id else None
