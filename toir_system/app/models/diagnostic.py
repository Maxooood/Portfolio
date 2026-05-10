from datetime import datetime, timezone
from app.extensions import db


class Diagnostic(db.Model):
    __tablename__ = 'diagnostics'

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.id'), unique=True, nullable=False)
    performed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    performed_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    cause = db.Column(db.Text, nullable=False)
    methods_used = db.Column(db.Text)
    tools_used = db.Column(db.Text)
    repair_required = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)

    request = db.relationship('Request', back_populates='diagnostic')
    performed_by = db.relationship('User')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'request_id': self.request_id,
            'performed_by_id': self.performed_by_id,
            'performed_by_name': self.performed_by.full_name if self.performed_by else None,
            'performed_at': self.performed_at.isoformat() if self.performed_at else None,
            'cause': self.cause,
            'methods_used': self.methods_used,
            'tools_used': self.tools_used,
            'repair_required': self.repair_required,
            'notes': self.notes,
        }

    def __repr__(self) -> str:
        return f'<Diagnostic for request {self.request_id}>'
