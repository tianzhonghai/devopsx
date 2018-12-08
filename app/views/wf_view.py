from flask import Blueprint, render_template, abort, jsonify, request
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from ..models import Deploy, BizApp, WfTask, WfTaskHist
from .. import db
from ..utils import common_util, data_dicts
from app.service import wf_service
from ..tasks import web_app_task


wf_view = Blueprint('wf_view', __name__, template_folder='templates')


@wf_view.route('/wf/todotasklist')
@login_required
def todo_task_list():
    try:
        return render_template('wf/todotasklist.html')
    except TemplateNotFound:
        abort(404)


@wf_view.route('/wf/gettodotasklist')
@login_required
def get_todo_task_list():
    current_user_id = current_user.userid
    limitstr = request.values.get("limit")
    offsetstr = request.values.get("offset")
    limit = 10
    if limitstr.strip():
        limit = int(limitstr)
    offset = 0
    if offsetstr.strip():
        offset = int(offsetstr)
    page = offset / limit + 1

    dtos = []
    task_proxy_result = db.session.execute("""SELECT A.*, B.app_id, B.app_version, B.env_id 
    FROM wf_task A JOIN biz_deploy B ON A.deploy_id = B.deploy_id 
    WHERE A.assignee_id = :assignee_id LIMIT :start, :limit""",
                                           {'assignee_id': current_user_id, 'start': offset, 'limit': limit})

    for rp in task_proxy_result:
        app_id = rp.app_id
        vo = {"app_id": app_id, "app_version": rp.app_version, "env_id": rp.env_id,
              "created_at": rp.created_at.strftime('%Y-%m-%d %H:%M:%S'), "act_name": rp.act_name,
              "act_type": rp.act_type, "task_id": rp.task_id }
        dtos.append(vo)

    task_proxy_result.close()

    count_proxy_result = db.session.execute("SELECT COUNT(*) as total FROM wf_task WHERE assignee_id=:assignee_id",
                                            {'assignee_id': current_user_id})
    count_proxy_result_fetchone = count_proxy_result.fetchone()
    count_proxy_result.close()
    db.session.close()
    total = count_proxy_result_fetchone.total

    return jsonify({"total": total, "rows": dtos})

    # pagination = Deploy.Deploy.query.filter(Deploy.Deploy.deploy_result == 0).paginate(page, per_page=limit, error_out=False)
    # items = pagination.items
    # vos = []
    # for item in items:
    #    vo = {"app_id": item.app_id, "app_version": item.app_version, "env_id": item.env_id,
    #         "deploy_result": item.deploy_result, "created_at": item.created_at.strftime('%Y-%m-%d %H:%M:%S'), "created_by": item.creator_account}
    #    vos.append(vo)

    # return jsonify({"total": pagination.total, "rows": vos})


@wf_view.route('/wf/adddeploy')
@login_required
def add_deploy():
    return render_template('wf/adddeploy.html')


@wf_view.route('/wf/adddeploysuccess', methods=['POST'])
@login_required
def add_deploy_success():
    result = {"status": 200, "message": ""}
    current_user_id = current_user.userid
    current_user_name = current_user.account
    appid = request.values.get('appid')
    envid = request.values.get('envid')
    version = None
    wf_service.create_deploy_task(appid, envid, version, current_user_id, current_user_name)
    return jsonify(result)


@wf_view.route('/wf/confirmversiontask')
@login_required
def confirm_version_task():
    taskid = request.values.get("taskid")
    task_model = WfTask.WfTask.query.filter(WfTask.WfTask.task_id == taskid).first()
    if task_model is None:
        abort(500)

    if current_user.type != 3:
        abort(403)

    if task_model.act_type != data_dicts.WfActivityConst.confirmVersion:
        abort(500)

    deploy_model = Deploy.Deploy.query.filter(Deploy.Deploy.deploy_id == task_model.deploy_id).first()
    return render_template('wf/confirmversiontask.html', deploy=deploy_model, task=task_model)


@wf_view.route('/wf/confirmversiontasksuccess', methods=['POST'])
@login_required
def confirm_version_task_success():
    result = {"status": 200, "message": ""}
    version = request.values.get('app_version')
    deploy_id = request.values.get('deploy_id')
    task_id = request.values.get('task_id')
    app_id = request.values.get('app_id')
    if version is None:
        result["status"] = 500
        result["message"] = "提交的数据不正确"

    wf_service.confirm_version_task(task_id, deploy_id, app_id, version)
    return jsonify(result)


@wf_view.route('/wf/confirmpublishtask')
@login_required
def confirm_publish_task():
    taskid = request.values.get("taskid")
    task_model = WfTask.WfTask.query.filter(WfTask.WfTask.task_id == taskid).first()
    if task_model is None:
        abort(500)

    if current_user.type != 2:
        abort(403)

    if task_model.act_type != data_dicts.WfActivityConst.confirmPublish:
        abort(500)

    if task_model.assignee_id != current_user.userid:
        abort(403)

    deploy_model = Deploy.Deploy.query.filter(Deploy.Deploy.deploy_id == task_model.deploy_id).first()
    return render_template('wf/confirmpublishtask.html', deploy=deploy_model, task=task_model)


@wf_view.route('/wf/confirmpublishtasksuccess', methods=['POST'])
@login_required
def confirm_publish_task_success():
    result = {"status": 200, "message": ""}
    deploy_id = request.values.get('deploy_id')
    task_id = request.values.get('task_id')
    app_id = request.values.get('app_id')

    wf_service.confirm_publish_task(task_id, deploy_id, app_id)

    bizapp = BizApp.BizApp.query.filter(BizApp.BizApp.app_id == app_id).first()
    # 调用celery开始发布
    # web_app_task.deploy_app_task_async.delay(deploy_id=deploy_id, bizapp=bizapp)
    web_app_task.deploy_app_task_async(deploy_id, bizapp)
    return jsonify(result)


@wf_view.route('/wf/testdeploy')
@login_required
def test_deploy():
    taskid = request.values.get("taskid")
    task_model = WfTask.WfTask.query.filter(WfTask.WfTask.task_id == taskid).first()
    deploy_model = Deploy.Deploy.query.filter(Deploy.Deploy.deploy_id == task_model.deploy_id).first()
    return render_template('/wf/testdeploy.html', deploy=deploy_model, task=task_model)


@wf_view.route('/wf/testdeploysuccess')
@login_required
def test_deploy_success():
    result = {"status": 200, "message": ""}
    deploy_id = request.values.get('deploy_id')
    task_id = request.values.get('task_id')
    app_id = request.values.get('app_id')

    return jsonify(result)
