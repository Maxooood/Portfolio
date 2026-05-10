from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app.api import api_bp
from app.models.user import UserRole
from app.models.audit import AuditLog
from app.utils.decorators import roles_required


@api_bp.route('/audit-log', methods=['GET'])
@roles_required(UserRole.ADMIN, UserRole.MANAGER)
def get_audit_log():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    action_filter = request.args.get('action')
    entity_filter = request.args.get('entity_type')

    query = AuditLog.query
    if action_filter:
        query = query.filter_by(action=action_filter)
    if entity_filter:
        query = query.filter_by(entity_type=entity_filter)

    pagination = query.order_by(AuditLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'items': [entry.to_dict() for entry in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
    }), 200
