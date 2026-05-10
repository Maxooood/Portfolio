import logging
from app.models.service import RoutingRule

logger = logging.getLogger(__name__)


def route_request(fault_type_id: int | None) -> int | None:
    """
    Automatically assigns a request to an auxiliary service based on routing rules.
    Returns service_id or None if no rule found.
    """
    if fault_type_id is None:
        logger.warning('route_request called with no fault_type_id — cannot auto-route')
        return None

    rule = (
        RoutingRule.query
        .filter_by(fault_type_id=fault_type_id, is_active=True)
        .order_by(RoutingRule.priority.asc())
        .first()
    )

    if rule:
        logger.info(
            f'Auto-routed fault_type={fault_type_id} to service={rule.service_id} '
            f'via rule={rule.id} (priority={rule.priority})'
        )
        return rule.service_id

    logger.warning(f'No active routing rule found for fault_type_id={fault_type_id}')
    return None
