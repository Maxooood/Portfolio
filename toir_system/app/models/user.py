from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class UserRole:
    SHIFT_MANAGER = 'shift_manager'
    EXECUTOR = 'executor'
    DISPATCHER = 'dispatcher'
    MANAGER = 'manager'
    ADMIN = 'admin'

    ALL = [SHIFT_MANAGER, EXECUTOR, DISPATCHER, MANAGER, ADMIN]


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    employee_number = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(30), nullable=False, default=UserRole.EXECUTOR)
    department = db.Column(db.String(100))
    phone = db.Column(db.String(30))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime(timezone=True))

    initiated_requests = db.relationship('Request', foreign_keys='Request.initiator_id', back_populates='initiator')
    assigned_requests = db.relationship('Request', foreign_keys='Request.executor_id', back_populates='executor')

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'employee_number': self.employee_number,
            'full_name': self.full_name,
            'email': self.email,
            'role': self.role,
            'department': self.department,
            'phone': self.phone,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f'<User {self.employee_number} ({self.role})>'
