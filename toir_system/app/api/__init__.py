from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

from app.api import auth, requests, equipment, services, users, analytics, admin  # noqa: E402, F401
