from datetime import datetime, timezone
from app.extensions import db
from app.models.audit import AuditLog


def generate_request_number() -> str:
    from app.models.request import Request
    today = datetime.now(timezone.utc)
    prefix = today.strftime('REQ-%Y%m%d-')
    last = (
        Request.query
        .filter(Request.request_number.like(f'{prefix}%'))
        .order_by(Request.id.desc())
        .first()
    )
    seq = 1
    if last:
        try:
            seq = int(last.request_number.split('-')[-1]) + 1
        except (ValueError, IndexError):
            seq = 1
    return f'{prefix}{seq:04d}'


def log_audit(user_id: int | None, action: str, entity_type: str = None,
              entity_id: int = None, details: str = None, ip_address: str = None) -> None:
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=ip_address,
    )
    db.session.add(entry)
