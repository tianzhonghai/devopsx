from flask_login import UserMixin
from flask_login._compat import text_type
from .. import db, login_manager


class User(db.Model, UserMixin):
    __tablename__ = 'sys_user'
    userid = db.Column("user_id", db.Integer, primary_key=True, autoincrement=True)
    account = db.Column("account", db.String(45), unique=False, nullable=False)
    passwordhash = db.Column("password_hash", db.String(45), unique=False, nullable=False)
    type = db.Column(db.Integer, nullable=True)

    def __init__(self, account, passwordhash, type):
        self.account = account
        self.passwordhash = passwordhash
        self.type = type

    def __repr__(self):
        return '<User %r>' % self.account

    def get_id(self):
        try:
            return text_type(self.userid)
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')
