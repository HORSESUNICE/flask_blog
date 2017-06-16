import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'any epsilon is greater than 0'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = \
        'mysql+pymysql://root:password@localhost/flask_blog'
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'yourqq@qq.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'password'
    MAIL_SUBJECT_PREFIX = '[Epsilon]'
    MAIL_SENDER = 'Epsilon <yourqq@qq.com>'
    ADMIN = os.environ.get('ADMIN') or 'yourqq@qq.com'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = \
        'mysql+pymysql://root:password@localhost/flask_blog_test'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = \
        'mysql+pymysql://root:password@localhost/flask_blog_product'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}