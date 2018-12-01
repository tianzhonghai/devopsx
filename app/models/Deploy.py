from .. import db


class Deploy(db.Model):
    __tablename__ = 'biz_deploy'
    deploy_id = db.Column("deploy_id", db.Integer, primary_key=True, autoincrement=True)
    app_id = db.Column("app_id", db.String(64), unique=False, nullable=False)
    app_version = db.Column("app_version", db.String(45), unique=False, nullable=False)
    env_id = db.Column("env_id", db.String(10), unique=False, nullable=False)
    creator_id = db.Column("creator_id", db.Integer, unique=False, nullable=False)
    creator_account = db.Column("creator_account", db.String(45), unique=False, nullable=False)
    created_at = db.Column("created_at", db.DateTime, unique=False, nullable=False)
    deploy_result = db.Column("deploy_result", db.Integer, nullable=False)
    deploy_result_info = db.Column("deploy_result_info", db.String(64), nullable=False)
    wf_status = db.Column("wf_status", db.String(32), nullable=False)

    def __init__(self, app_id, app_version, env_id,
                 creator_id, creator_account, created_at, deploy_result, deploy_result_info, wf_status):
        self.app_id = app_id
        self.app_version = app_version
        self.env_id = env_id
        self.creator_id = creator_id
        self.creator_account = creator_account
        self.created_at = created_at
        self.deploy_result = deploy_result
        self.deploy_result_info = deploy_result_info
        self.wf_status = wf_status
