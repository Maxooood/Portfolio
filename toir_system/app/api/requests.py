from datetime import datetime, timezone
from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import api_bp
from app.extensions import db
from app.models.request import Request, RequestStatus, StatusHistory
from app.models.diagnostic import Diagnostic
from app.models.repair import Repair, RepairMaterial
from app.models.report import Report
from app.models.user import User, UserRole
from app.utils.decorators import roles_required, get_current_user
from app.utils.helpers import generate_request_number, log_audit
from app.services.routing import route_request


@api_bp.route('/requests', methods=['GET'])
@jwt_required()
def list_requests():
    user = get_current_user()
    query = Request.query

    if user.role == UserRole.SHIFT_MANAGER:
        query = query.filter_by(initiator_id=user.id)
    elif user.role == UserRole.EXECUTOR:
        query = query.filter_by(executor_id=user.id)

    status = request.args.get('status')
    priority = request.args.get('priority')
    service_id = request.args.get('service_id', type=int)
    fault_type_id = request.args.get('fault_type_id', type=int)

    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)
    if service_id:
        query = query.filter_by(service_id=service_id)
    if fault_type_id:
        query = query.filter_by(fault_type_id=fault_type_id)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = query.order_by(Request.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [r.to_dict(include_relations=True) for r in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
    }), 200


@api_bp.route('/requests/<int:req_id>', methods=['GET'])
@jwt_required()
def get_request(req_id):
    req = Request.query.get_or_404(req_id)
    data = req.to_dict(include_relations=True)
    data['status_history'] = [h.to_dict() for h in req.status_history]
    data['diagnostic'] = req.diagnostic.to_dict() if req.diagnostic else None
    data['repair'] = req.repair.to_dict() if req.repair else None
    data['report'] = req.report.to_dict() if req.report else None
    return jsonify(data), 200


@api_bp.route('/requests', methods=['POST'])
@roles_required(UserRole.SHIFT_MANAGER, UserRole.DISPATCHER, UserRole.ADMIN)
def create_request():
    user = get_current_user()
    data = request.get_json()

    required = ['title', 'description', 'equipment_id']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Поле {field} обязательно'}), 400

    req_number = generate_request_number()
    fault_type_id = data.get('fault_type_id')
    service_id = data.get('service_id') or route_request(fault_type_id)

    new_request = Request(
        request_number=req_number,
        title=data['title'],
        description=data['description'],
        priority=data.get('priority', 'medium'),
        fault_type_id=fault_type_id,
        equipment_id=data['equipment_id'],
        initiator_id=user.id,
        service_id=service_id,
        notes=data.get('notes'),
        status=RequestStatus.NEW,
    )
    db.session.add(new_request)
    db.session.flush()

    history = StatusHistory(
        request_id=new_request.id,
        old_status=None,
        new_status=RequestStatus.NEW,
        changed_by_id=user.id,
        comment='Заявка создана',
    )
    db.session.add(history)
    log_audit(user.id, 'REQUEST_CREATED', 'request', new_request.id,
              details=f'number={req_number}', ip_address=request.remote_addr)
    db.session.commit()

    current_app.logger.info(f'Request {req_number} created by user {user.employee_number}')
    return jsonify(new_request.to_dict()), 201


@api_bp.route('/requests/<int:req_id>', methods=['PUT'])
@roles_required(UserRole.SHIFT_MANAGER, UserRole.DISPATCHER, UserRole.ADMIN)
def update_request(req_id):
    user = get_current_user()
    req = Request.query.get_or_404(req_id)

    if user.role == UserRole.SHIFT_MANAGER and req.initiator_id != user.id:
        return jsonify({'error': 'Нет доступа к этой заявке'}), 403

    if req.status not in [RequestStatus.NEW, RequestStatus.ASSIGNED]:
        return jsonify({'error': 'Редактирование возможно только для заявок в статусе "Новая" или "Назначена"'}), 400

    data = request.get_json()
    for field in ['title', 'description', 'priority', 'notes', 'fault_type_id', 'equipment_id']:
        if field in data:
            setattr(req, field, data[field])

    log_audit(user.id, 'REQUEST_UPDATED', 'request', req.id, ip_address=request.remote_addr)
    db.session.commit()
    current_app.logger.info(f'Request {req.request_number} updated by {user.employee_number}')
    return jsonify(req.to_dict()), 200


@api_bp.route('/requests/<int:req_id>/status', methods=['PUT'])
@jwt_required()
def update_status(req_id):
    user = get_current_user()
    req = Request.query.get_or_404(req_id)
    data = request.get_json()
    new_status = data.get('status')
    comment = data.get('comment')

    if not new_status:
        return jsonify({'error': 'Поле status обязательно'}), 400

    if not RequestStatus.can_transition(req.status, new_status):
        return jsonify({
            'error': f'Переход из статуса "{req.status}" в "{new_status}" недопустим'
        }), 400

    # Role checks per transition
    role = user.role
    if new_status == RequestStatus.ASSIGNED and role not in [UserRole.DISPATCHER, UserRole.ADMIN]:
        return jsonify({'error': 'Назначить заявку может только диспетчер'}), 403
    if new_status in [RequestStatus.IN_PROGRESS, RequestStatus.DIAGNOSTICS_DONE,
                      RequestStatus.REPAIR_IN_PROGRESS, RequestStatus.COMPLETED]:
        if role not in [UserRole.EXECUTOR, UserRole.DISPATCHER, UserRole.ADMIN]:
            return jsonify({'error': 'Изменить этот статус может только исполнитель или диспетчер'}), 403
    if new_status == RequestStatus.CLOSED and role not in [UserRole.DISPATCHER, UserRole.ADMIN]:
        return jsonify({'error': 'Закрыть заявку может только диспетчер'}), 403

    old_status = req.status
    req.status = new_status
    now = datetime.now(timezone.utc)

    if new_status == RequestStatus.IN_PROGRESS and not req.started_at:
        req.started_at = now
    if new_status == RequestStatus.COMPLETED:
        req.completed_at = now
    if new_status == RequestStatus.CLOSED:
        req.closed_at = now

    if new_status == RequestStatus.ASSIGNED and data.get('executor_id'):
        req.executor_id = data['executor_id']
    if new_status == RequestStatus.ASSIGNED and data.get('service_id'):
        req.service_id = data['service_id']

    history = StatusHistory(
        request_id=req.id,
        old_status=old_status,
        new_status=new_status,
        changed_by_id=user.id,
        comment=comment,
    )
    db.session.add(history)
    log_audit(user.id, 'REQUEST_STATUS_CHANGED', 'request', req.id,
              details=f'{old_status} -> {new_status}', ip_address=request.remote_addr)
    db.session.commit()

    current_app.logger.info(
        f'Request {req.request_number}: {old_status} -> {new_status} by {user.employee_number}'
    )
    return jsonify(req.to_dict()), 200


@api_bp.route('/requests/<int:req_id>/diagnostic', methods=['POST'])
@roles_required(UserRole.EXECUTOR, UserRole.DISPATCHER, UserRole.ADMIN)
def add_diagnostic(req_id):
    user = get_current_user()
    req = Request.query.get_or_404(req_id)

    if req.status != RequestStatus.IN_PROGRESS:
        return jsonify({'error': 'Диагностика возможна только для заявок в статусе "В работе"'}), 400
    if req.diagnostic:
        return jsonify({'error': 'Диагностика уже добавлена для этой заявки'}), 409

    data = request.get_json()
    if not data.get('cause'):
        return jsonify({'error': 'Поле cause (причина) обязательно'}), 400

    diagnostic = Diagnostic(
        request_id=req.id,
        performed_by_id=user.id,
        cause=data['cause'],
        methods_used=data.get('methods_used'),
        tools_used=data.get('tools_used'),
        repair_required=data.get('repair_required', True),
        notes=data.get('notes'),
    )
    db.session.add(diagnostic)

    req.status = RequestStatus.DIAGNOSTICS_DONE
    history = StatusHistory(
        request_id=req.id,
        old_status=RequestStatus.IN_PROGRESS,
        new_status=RequestStatus.DIAGNOSTICS_DONE,
        changed_by_id=user.id,
        comment='Диагностика выполнена',
    )
    db.session.add(history)
    log_audit(user.id, 'DIAGNOSTIC_ADDED', 'request', req.id, ip_address=request.remote_addr)
    db.session.commit()

    current_app.logger.info(f'Diagnostic added to request {req.request_number}')
    return jsonify(diagnostic.to_dict()), 201


@api_bp.route('/requests/<int:req_id>/repair', methods=['POST'])
@roles_required(UserRole.EXECUTOR, UserRole.DISPATCHER, UserRole.ADMIN)
def add_repair(req_id):
    user = get_current_user()
    req = Request.query.get_or_404(req_id)

    if req.status not in [RequestStatus.DIAGNOSTICS_DONE, RequestStatus.REPAIR_IN_PROGRESS]:
        return jsonify({'error': 'Ремонт возможен только после диагностики'}), 400
    if req.repair:
        return jsonify({'error': 'Ремонт уже добавлен для этой заявки'}), 409

    data = request.get_json()
    if not data.get('operations'):
        return jsonify({'error': 'Поле operations (выполненные работы) обязательно'}), 400

    repair = Repair(
        request_id=req.id,
        performed_by_id=user.id,
        operations=data['operations'],
        labor_hours=data.get('labor_hours'),
        notes=data.get('notes'),
    )
    db.session.add(repair)
    db.session.flush()

    for mat in data.get('materials', []):
        material = RepairMaterial(
            repair_id=repair.id,
            name=mat['name'],
            quantity=mat.get('quantity', 1),
            unit=mat.get('unit'),
            cost=mat.get('cost'),
        )
        db.session.add(material)

    req.status = RequestStatus.REPAIR_IN_PROGRESS
    if data.get('completed', False):
        repair.completed_at = datetime.now(timezone.utc)
        req.status = RequestStatus.COMPLETED
        req.completed_at = datetime.now(timezone.utc)

    history = StatusHistory(
        request_id=req.id,
        old_status=RequestStatus.DIAGNOSTICS_DONE,
        new_status=req.status,
        changed_by_id=user.id,
        comment='Ремонт выполнен' if data.get('completed') else 'Ремонт начат',
    )
    db.session.add(history)
    log_audit(user.id, 'REPAIR_ADDED', 'request', req.id, ip_address=request.remote_addr)
    db.session.commit()

    current_app.logger.info(f'Repair added to request {req.request_number}')
    return jsonify(repair.to_dict()), 201


@api_bp.route('/requests/<int:req_id>/report', methods=['POST'])
@roles_required(UserRole.EXECUTOR, UserRole.DISPATCHER, UserRole.ADMIN)
def add_report(req_id):
    user = get_current_user()
    req = Request.query.get_or_404(req_id)

    if req.status not in [RequestStatus.COMPLETED, RequestStatus.CLOSED]:
        return jsonify({'error': 'Отчет формируется только для выполненных заявок'}), 400
    if req.report:
        return jsonify({'error': 'Отчет уже сформирован для этой заявки'}), 409

    data = request.get_json()
    for field in ['summary', 'conclusion']:
        if not data.get(field):
            return jsonify({'error': f'Поле {field} обязательно'}), 400

    report = Report(
        request_id=req.id,
        created_by_id=user.id,
        summary=data['summary'],
        conclusion=data['conclusion'],
        recommendations=data.get('recommendations'),
    )
    db.session.add(report)
    log_audit(user.id, 'REPORT_CREATED', 'request', req.id, ip_address=request.remote_addr)
    db.session.commit()

    current_app.logger.info(f'Report created for request {req.request_number}')
    return jsonify(report.to_dict()), 201
