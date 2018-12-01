from flask import Blueprint, render_template, abort, jsonify, request
from jinja2 import TemplateNotFound
from ..models import User, UserType
from flask_login import login_required
from .. import db, login_manager
import hashlib


user_view = Blueprint('user_view', __name__, template_folder='templates')


@user_view.route('/user/index')
@login_required
def index(page=1):
    try:
        return render_template('sys/userlist.html')
    except TemplateNotFound:
        abort(404)


@user_view.route('/user/getuserlist')
@login_required
def get_user_list():
    limitstr = request.values.get("limit")
    offsetstr = request.values.get("offset")
    limit = 10
    if limitstr.strip():
        limit = int(limitstr)
    offset = 0
    if offsetstr.strip():
        offset = int(offsetstr)
    page = offset / limit + 1
    pagination = User.User.query.paginate(page, per_page=limit, error_out=False)
    userEntities = pagination.items
    userVOs = []
    for userEntity in userEntities:
        typestr = UserType.UserType.convert_to_desc(userEntity.type)
        uservo = {"userid": userEntity.userid, "account": userEntity.account, "type": userEntity.type, "typedisplay": typestr}
        userVOs.append(uservo)

    return jsonify({"total": pagination.total, "rows": userVOs })


@user_view.route('/user/add', methods=['GET'])
@login_required
def add():
    return render_template("sys/adduser.html")


@user_view.route('/user/addsuccess', methods=['POST'])
@login_required
def add_success():
    result = {"status": 200, "message": ""}
    account = request.values.get('account')
    usertype = request.values.get('type')
    # 判断用户是否存在
    user = User.User.query.filter(User.User.account == account).first()
    if user is not None:
        result["status"] = 500
        result["message"] = "用户已存在"
        return jsonify(result)
    pwd = "12345678".encode()
    pwdhash = hashlib.md5(pwd).hexdigest()
    newuser = User.User(account=account, passwordhash=pwdhash, type=usertype)
    db.session.add(newuser)
    db.session.commit()
    db.session.close()
    return jsonify(result)


@login_manager.user_loader
def load_user(userid):
    return User.User.query.filter(User.User.userid == userid).first()
