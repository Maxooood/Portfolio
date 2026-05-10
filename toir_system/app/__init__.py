import os
from flask import Flask, jsonify
from app.config import config
from app.extensions import db, migrate, jwt
from app.logging_config import setup_logging


def create_app(config_name: str = None) -> Flask:
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    setup_logging(app)

    from app.api import api_bp
    app.register_blueprint(api_bp)

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Ресурс не найден'}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'error': 'Метод не разрешён'}), 405

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f'Internal server error: {e}')
        return jsonify({'error': 'Внутренняя ошибка сервера'}), 500

    @app.route('/')
    def index():
        return jsonify({
            'status': 'ok',
            'message': 'TOIR System API',
            'endpoints': {
                'health': '/health',
                'api': '/api',
                'auth': '/api/auth/login',
            }
        }), 200

    @app.route('/health')
    def health_check():
        return jsonify({'status': 'ok'}), 200

    with app.app_context():
        from app import models as _models  # noqa: F401

    app.logger.info(f'Application created with config={config_name}')
    return app
