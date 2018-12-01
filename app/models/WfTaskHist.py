from .. import db


class WfTaskHist(db.Model):
    __tablename__ = 'wf_task_hist'
    id = db.Column("id", db.Integer, primary_key=True, autoincrement=True)
    deploy_id = db.Column("deploy_id", db.Integer, unique=False, nullable=False)
    act_name = db.Column("act_name", db.String(45), unique=False, nullable=False)
    act_type = db.Column("act_type", db.String(45), unique=False, nullable=False)
    assignee_id = db.Column("assignee_id", db.Integer, unique=False, nullable=False)
    assignee_account = db.Column("assignee_account", db.String(45), unique=False, nullable=False)
    created_at = db.Column("created_at", db.DateTime, unique=False, nullable=False)

    def __init__(self, deploy_id, act_name, act_type, assignee_id, assignee_account, created_at):
        self.deploy_id = deploy_id
        self.act_name = act_name
        self.act_type = act_type
        self.assignee_id = assignee_id
        self.assignee_account = assignee_account
        self.created_at = created_at
