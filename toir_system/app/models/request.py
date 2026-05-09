from datetime import datetime, timezone
from app.extensions import db


class RequestStatus:
    NEW = 'new'
    ASSIGNED = 'assigned'
    IN_PROGRESS = 'in_progress'
    DIAGNOSTICS_DONE = 'diagnostics_done'
    REPAIR_IN_PROGRESS = 'repair_in_progress'
    COMPLETED = 'completed'
    CLOSED = 'closed'
    CANCELLED = 'cancelled'

    ALL = [NEW, ASSIGNED, IN_PROGRESS, DIAGNOSTICS_DONE, REPAIR_IN_PROGRESS, COMPLETED, CLOSED, CANCELLED]

    ALLOWED_TRANSITIONS = {
        NEW: [ASSIGNED, CANCELLED],
        ASSIGNED: [IN_PROGRESS, CANCELLED],
        IN_PROGRESS: [DIAGNOSTICS_DONE, CANCELLED],
        DIAGNOSTICS_DONE: [REPAIR_IN_PROGRESS, COMPLETED],
        REPAIR_IN_PROGRESS: [COMPLETED],
        COMPLETED: [CLOSED],
        CLOSED: [],
        CANCELLED: [],
    }

    @classmethod
    def can_transition(cls, from_status: str, to_status: str) -> bool:
        return to_status in cls.ALLOWED_TRANSITIONS.get(from_status, [])


class RequestPriority:
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class Request(db.Model):
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True)
    request_number = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default=RequestPriority.MEDIUM, nullable=False)
    status = db.Column(db.String(30), default=RequestStatus.NEW, nullable=False)

    fault_type_id = db.Column(db.Integer, db.ForeignKey('fault_types.id'))
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    initiator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('auxiliary_services.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))
    started_at = db.Column(db.DateTime(timezone=True))
    completed_at = db.Column(db.DateTime(timezone=True))
    closed_at = db.Column(db.DateTime(timezone=True))

    fault_type = db.relationship('FaultType', back_populates='requests')
    equipment = db.relationship('Equipment', back_populates='requests')
    initiator = db.relationship('User', foreign_keys=[initiator_id], back_populates='initiated_requests')
    executor = db.relationship('User', foreign_keys=[executor_id], back_populates='assigned_requests')
    service = db.relationship('AuxiliaryService', back_populates='requests')
    status_history = db.relationship('StatusHistory', back_populates='request', order_by='StatusHistory.changed_at')
    diagnostic = db.relationship('Diagnostic', back_populates='request', uselist=False)
    repair = db.relationship('Repair', back_populates='request', uselist=False)
    report = db.relationship('Report', back_populates='request', uselist=False)

    def to_dict(self, include_relations: bool = False) -> dict:
        data = {
            'id': self.id,
            'request_number': self.request_number,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'fault_type_id': self.fault_type_id,
            'equipment_id': self.equipment_id,
            'initiator_id': self.initiator_id,
            'service_id': self.service_id,
            'executor_id': self.executor_id,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
        }
        if include_relations:
            data['equipment'] = self.equipment.to_dict() if self.equipment else None
            data['initiator'] = self.initiator.to_dict() if self.initiator else None
            data['service'] = self.service.to_dict() if self.service else None
            data['fault_type'] = self.fault_type.to_dict() if self.fault_type else None
        return data

    def __repr__(self) -> str:
        return f'<Request {self.request_number} [{self.status}]>'


class StatusHistory(db.Model):
    __tablename__ = 'status_history'

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.id'), nullable=False)
    old_status = db.Column(db.String(30))
    new_status = db.Column(db.String(30), nullable=False)
    changed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    changed_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    comment = db.Column(db.Text)

    request = db.relationship('Request', back_populates='status_history')
    changed_by = db.relationship('User')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'request_id': self.request_id,
            'old_status': self.old_status,
            'new_status': self.new_status,
            'changed_by_id': self.changed_by_id,
            'changed_by_name': self.changed_by.full_name if self.changed_by else None,
            'changed_at': self.changed_at.isoformat() if self.changed_at else None,
            'comment': self.comment,
        }
