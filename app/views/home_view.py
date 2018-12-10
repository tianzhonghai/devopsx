from flask import (Blueprint, render_template, abort, request, redirect, url_for, flash)
from jinja2 import TemplateNotFound
from .. import login_manager
from ..models import User
from flask_login import login_user, logout_user
import hashlib
from .. import db
from ..utils import common_util, data_dicts


home_view = Blueprint('home_view', __name__)


@home_view.route("/")
def index():
    try:
        return render_template('home/index.html')
    except TemplateNotFound:
        abort(404)


@home_view.route('/getrecentdeploylist')
def get_recent_deploy_list():
    limitstr = request.values.get("limit")
    offsetstr = request.values.get("offset")
    limit = 10
    if limitstr.strip():
        limit = int(limitstr)
    offset = 0
    if offsetstr.strip():
        offset = int(offsetstr)
    # page = offset / limit + 1

    task_proxy_result = db.session.execute(
        """SELECT * FROM biz_deploy WHERE wf_status IN ('Publishing','Published','Test') ORDER BY deploy_id DESC LIMIT :start, :limit""",
        {'start': offset, 'limit': limit})
    dtos = []
    for rp in task_proxy_result:
        vo = {"app_id": rp.app_id, "app_version": rp.app_version, "env_id": rp.env_id,
              "deploy_result": data_dicts.DeployResultEnum.convert_to_desc(rp.deploy_result),
              "created_at": rp.created_at.strftime('%Y-%m-%d %H:%M:%S'),
              "created_by": rp.creator_account, "wf_status": rp.wf_status}
        dtos.append(vo)

    task_proxy_result.close()

    count_proxy_result = db.session.execute(
        "SELECT COUNT(*) as total FROM biz_deploy WHERE wf_status IN ('Publishing','Published','Test')")
    count_proxy_result_fetchone = count_proxy_result.fetchone()
    count_proxy_result.close()
    db.session.close()
    total = count_proxy_result_fetchone.total

    return jsonify({"total": total, "rows": dtos})



@home_view.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        account = request.values.get("account")
        pwd = request.values.get("password")
        pwd = pwd.encode()
        pwdhash = hashlib.md5(pwd)
        user = User.User.query.filter(User.User.account == account).first()
        if user is None:
            flash("用户不存在")
        elif user.passwordhash != pwdhash.hexdigest():
            flash("用户名或密码不存在")
        else:
            login_user(user)
            # return redirect(url_for('home_view.index'))
            return redirect(url_for('deploy_view.pending_list'))

    return render_template('home/login.html')


@home_view.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('home_view.index'))


@login_manager.user_loader
def load_user(userid):
    return User.User.query.filter(User.User.userid == userid).first()
