from .. import db


class BizApp(db.Model):
    __tablename__ = "biz_app"
    app_id = db.Column("app_id", db.String(64), primary_key=True, autoincrement=False, unique=True, nullable=False)
    internal_ips = db.Column("internal_ips", db.String(256), unique=False, nullable=False)
    dev_id = db.Column("dev_id", db.Integer, unique=False, nullable=False)
    dev_account = db.Column("dev_account", db.String(45), unique=False, nullable=False)
    test_id = db.Column("test_id", db.Integer, unique=False, nullable=False)
    test_account = db.Column("test_account", db.String(45), unique=False, nullable=False)

    def __init__(self, app_id, internal_ips, dev_id, dev_account, test_id, test_account):
        self.app_id = app_id
        self.internal_ips = internal_ips
        self.dev_id = dev_id
        self.dev_account = dev_account
        self.test_id = test_id
        self.test_account = test_account
