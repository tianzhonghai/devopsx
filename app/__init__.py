from flask import Flask
from celery import Celery, platforms
from config import config, Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import logging


db = SQLAlchemy()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)
platforms.C_FORCE_ROOT = True

login_manager = LoginManager()


def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)

    celery.conf.update(app.config)

    login_manager.init_app(app)

    # 日志系统配置
    handler = logging.FileHandler('devops-file.log', encoding='UTF-8')
    app.logger.addHandler(handler)
    logging_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    handler.setFormatter(logging_format)
    app.logger.addHandler(handler)

    from .views.home_view import home_view as home_blueprint
    app.register_blueprint(home_blueprint)
    from .views.deploy_view import deploy_view as deploy_blueprint
    app.register_blueprint(deploy_blueprint)
    from .views.user_view import user_view as user_blueprint
    app.register_blueprint(user_blueprint)
    from .views.host_view import host_view as host_blueprint
    app.register_blueprint(host_blueprint)
    from .views.bizapp_view import bizapp_view as bizapp_blueprint
    app.register_blueprint(bizapp_blueprint)
    from .views.wf_view import wf_view as wf_blueprint
    app.register_blueprint(wf_blueprint)

    from .views.global_view import global_view as global_blueprint
    app.register_blueprint(global_blueprint)

    return app
