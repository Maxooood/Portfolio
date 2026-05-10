from datetime import datetime, timezone
from app.extensions import db


class Repair(db.Model):
    __tablename__ = 'repairs'

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.id'), unique=True, nullable=False)
    performed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    started_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime(timezone=True))
    operations = db.Column(db.Text, nullable=False)
    labor_hours = db.Column(db.Float)
    notes = db.Column(db.Text)

    request = db.relationship('Request', back_populates='repair')
    performed_by = db.relationship('User')
    materials = db.relationship('RepairMaterial', back_populates='repair', cascade='all, delete-orphan')

    def total_material_cost(self) -> float:
        return sum(m.cost * m.quantity for m in self.materials if m.cost)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'request_id': self.request_id,
            'performed_by_id': self.performed_by_id,
            'performed_by_name': self.performed_by.full_name if self.performed_by else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'operations': self.operations,
            'labor_hours': self.labor_hours,
            'notes': self.notes,
            'total_material_cost': self.total_material_cost(),
            'materials': [m.to_dict() for m in self.materials],
        }

    def __repr__(self) -> str:
        return f'<Repair for request {self.request_id}>'


class RepairMaterial(db.Model):
    __tablename__ = 'repair_materials'

    id = db.Column(db.Integer, primary_key=True)
    repair_id = db.Column(db.Integer, db.ForeignKey('repairs.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(30))
    cost = db.Column(db.Float)

    repair = db.relationship('Repair', back_populates='materials')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'repair_id': self.repair_id,
            'name': self.name,
            'quantity': self.quantity,
            'unit': self.unit,
            'cost': self.cost,
            'total_cost': self.cost * self.quantity if self.cost else None,
        }
