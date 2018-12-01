from .. import db


class BizTask(db.Model):
    __tablename__ = 'biz_task'
    task_id = db.Column("task_id", db.Integer, primary_key=True, autoincrement=True)
    deploy_id = db.Column("deploy_id", db.Integer, unique=False, nullable=False)
    result_status = db.Column("result_status", db.String(16), unique=False, nullable=False)
    task_name = db.Column("task_name", db.String(32), unique=False, nullable=False)
    host_name = db.Column("host_name", db.String(32), unique=False, nullable=False)
    result_info = db.Column("result_info", db.String(1000), unique=False, nullable=False)

    def __init__(self, deploy_id, result_status, task_name, host_name, result_info):
        self.deploy_id = deploy_id
        self.result_status = result_status
        self.task_name = task_name
        self.host_name = host_name
        self.result_info = result_info
