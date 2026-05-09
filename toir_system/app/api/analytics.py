from datetime import datetime
from flask import request, jsonify, current_app
from app.api import api_bp
from app.models.user import UserRole
from app.utils.decorators import roles_required
from app.services import analytics as analytics_service


@api_bp.route('/analytics/summary', methods=['GET'])
@roles_required(UserRole.MANAGER, UserRole.DISPATCHER, UserRole.ADMIN)
def summary():
    date_from_str = request.args.get('date_from')
    date_to_str = request.args.get('date_to')
    date_from = datetime.fromisoformat(date_from_str) if date_from_str else None
    date_to = datetime.fromisoformat(date_to_str) if date_to_str else None

    stats = analytics_service.get_summary_stats(date_from, date_to)
    current_app.logger.info(f'Analytics summary requested (date_from={date_from_str}, date_to={date_to_str})')
    return jsonify(stats), 200


@api_bp.route('/analytics/equipment-faults', methods=['GET'])
@roles_required(UserRole.MANAGER, UserRole.DISPATCHER, UserRole.ADMIN)
def equipment_faults():
    stats = analytics_service.get_equipment_fault_stats()
    return jsonify(stats), 200


@api_bp.route('/analytics/service-performance', methods=['GET'])
@roles_required(UserRole.MANAGER, UserRole.ADMIN)
def service_performance():
    stats = analytics_service.get_service_performance()
    return jsonify(stats), 200
