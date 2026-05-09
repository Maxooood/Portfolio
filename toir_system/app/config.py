import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'postgresql://toir_user:toir_pass@localhost:5432/toir_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    JSON_AS_ASCII = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL', 'postgresql://toir_user:toir_pass@localhost:5432/toir_test_db'
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)


config = {
    'development': Config,
    'testing': TestingConfig,
    'default': Config,
}
