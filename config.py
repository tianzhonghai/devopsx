import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:111111@192.168.1.4:3306/glaucusdb?charset=utf8'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    SECRET_KEY = 'devopsauth'

    CELERY_BROKER_URL = 'redis://:123456@192.168.1.9:6379/0'
    CELERY_RESULT_BACKEND = 'redis://:123456@192.168.1.9:6379/0'

    @staticmethod
    def init_app(app):
        pass


class DevConfig(Config):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'mysql+pymysql://root:mysql.com2017@106.14.96.72:3306/glaucus?charset=utf8'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'mysql+pymysql://test:111111@192.168.1.4:3306/glaucusdb?charset=utf8'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'mysql+pymysql://root:111111@192.168.1.4:3306/glaucusdb?charset=utf8'


config = {
    'development': DevConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevConfig
}
