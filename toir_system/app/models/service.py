from app.extensions import db


class AuxiliaryService(db.Model):
    __tablename__ = 'auxiliary_services'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    specialization = db.Column(db.String(200))
    contact_person = db.Column(db.String(200))
    contact_phone = db.Column(db.String(30))
    is_active = db.Column(db.Boolean, default=True)

    requests = db.relationship('Request', back_populates='service')
    routing_rules = db.relationship('RoutingRule', back_populates='service')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'specialization': self.specialization,
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'is_active': self.is_active,
        }

    def __repr__(self) -> str:
        return f'<AuxiliaryService {self.code}: {self.name}>'


class RoutingRule(db.Model):
    __tablename__ = 'routing_rules'

    id = db.Column(db.Integer, primary_key=True)
    fault_type_id = db.Column(db.Integer, db.ForeignKey('fault_types.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('auxiliary_services.id'), nullable=False)
    priority = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)

    fault_type = db.relationship('FaultType', back_populates='routing_rules')
    service = db.relationship('AuxiliaryService', back_populates='routing_rules')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'fault_type_id': self.fault_type_id,
            'fault_type_name': self.fault_type.name if self.fault_type else None,
            'service_id': self.service_id,
            'service_name': self.service.name if self.service else None,
            'priority': self.priority,
            'is_active': self.is_active,
        }

    def __repr__(self) -> str:
        return f'<RoutingRule fault_type={self.fault_type_id} -> service={self.service_id}>'
