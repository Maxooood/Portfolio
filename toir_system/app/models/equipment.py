from datetime import datetime, timezone
from app.extensions import db


class EquipmentStatus:
    OPERATIONAL = 'operational'
    UNDER_MAINTENANCE = 'under_maintenance'
    BROKEN = 'broken'
    DECOMMISSIONED = 'decommissioned'


class Equipment(db.Model):
    __tablename__ = 'equipment'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    inventory_number = db.Column(db.String(50), unique=True, nullable=False)
    equipment_type = db.Column(db.String(100))
    location = db.Column(db.String(200))
    department = db.Column(db.String(100))
    manufacturer = db.Column(db.String(100))
    model = db.Column(db.String(100))
    year_of_manufacture = db.Column(db.Integer)
    status = db.Column(db.String(30), default=EquipmentStatus.OPERATIONAL, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    requests = db.relationship('Request', back_populates='equipment')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'inventory_number': self.inventory_number,
            'equipment_type': self.equipment_type,
            'location': self.location,
            'department': self.department,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'year_of_manufacture': self.year_of_manufacture,
            'status': self.status,
        }

    def __repr__(self) -> str:
        return f'<Equipment {self.inventory_number}: {self.name}>'


class FaultType(db.Model):
    __tablename__ = 'fault_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)

    requests = db.relationship('Request', back_populates='fault_type')
    routing_rules = db.relationship('RoutingRule', back_populates='fault_type')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
        }

    def __repr__(self) -> str:
        return f'<FaultType {self.name}>'
