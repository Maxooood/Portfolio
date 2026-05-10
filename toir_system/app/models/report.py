from datetime import datetime, timezone
from app.extensions import db


class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.id'), unique=True, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    summary = db.Column(db.Text, nullable=False)
    conclusion = db.Column(db.Text, nullable=False)
    recommendations = db.Column(db.Text)

    request = db.relationship('Request', back_populates='report')
    created_by = db.relationship('User')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'request_id': self.request_id,
            'created_by_id': self.created_by_id,
            'created_by_name': self.created_by.full_name if self.created_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'summary': self.summary,
            'conclusion': self.conclusion,
            'recommendations': self.recommendations,
        }

    def __repr__(self) -> str:
        return f'<Report for request {self.request_id}>'
