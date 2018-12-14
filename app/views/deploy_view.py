from flask import Blueprint, render_template, abort, jsonify, request
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from ..models import Deploy
from .. import db
from ..utils import data_dicts


deploy_view = Blueprint('deploy_view', __name__, template_folder='templates')


@deploy_view.route('/deploy/querydeploy')
def query_deploy():
    try:
        return render_template('deploy/querydeploy.html')
    except TemplateNotFound:
        abort(404)


@deploy_view.route('/deploy/doquerydeploy')
def do_query_deploy():
    limitstr = request.values.get("limit")
    offsetstr = request.values.get("offset")
    if limitstr.strip():
        limit = int(limitstr)
    offset = 0
    if offsetstr.strip():
        offset = int(offsetstr)
    # page = offset / limit + 1
    appname = request.values.get('appname')
    sql_select = "SELECT * FROM biz_deploy WHERE wf_status = '"+data_dicts.WfActivityConst.complete+"'"
    sql_count = "SELECT COUNT(*) as total FROM biz_deploy WHERE wf_status = '"+data_dicts.WfActivityConst.complete+"'"
    if appname is not None and appname != '':
        sql_select += " AND app_id LIKE :appname"
        sql_count += " AND app_id LIKE :appname"

        sql_select += " ORDER BY deploy_id DESC LIMIT :start, :limit "

    params = {'start': offset, 'limit': limit, 'appname': '%'+appname+'%'}
    task_proxy_result = db.session.execute(sql_select, {'start': offset, 'limit': limit, 'appname': '%'+appname+'%'})
    dtos = []
    for rp in task_proxy_result:
        vo = {"app_id": rp.app_id, "app_version": rp.app_version, "env_id": rp.env_id,
              "deploy_result":data_dicts.DeployResultEnum.convert_to_desc(rp.deploy_result),
              "created_at": rp.created_at.strftime('%Y-%m-%d %H:%M:%S'),
              "created_by": rp.creator_account, "wf_status": rp.wf_status}
        dtos.append(vo)

    task_proxy_result.close()

    count_proxy_result = db.session.execute(sql_count, params)
    count_proxy_result_fetchone = count_proxy_result.fetchone()
    count_proxy_result.close()
    db.session.close()
    total = count_proxy_result_fetchone.total

    return jsonify({"total": total, "rows": dtos})
    # pagination = Deploy.Deploy.query.filter(Deploy.Deploy.wf_status._in(['Publishing', 'Published', 'Test']))
    # .paginate(page, per_page=limit, error_out=False)
    # items = pagination.items


@deploy_view.route('/deploy/listmyqlldeploy')
@login_required
def list_my_all_deploy():
    try:
        return render_template('deploy/listalldeploy.html')
    except TemplateNotFound:
        abort(404)


@deploy_view.route('/deploy/dolistmyalldeploy')
@login_required
def do_list_my_all_deploy():
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
    pagination = Deploy.Deploy.query.filter(Deploy.Deploy.creator_id == current_user_id)\
        .paginate(page, per_page=limit, error_out=False)
    items = pagination.items
    vos = []
    for item in items:
        vo = {"app_id": item.app_id, "app_version": item.app_version, "env_id": item.env_id,
              "deploy_result": data_dicts.DeployResultEnum.convert_to_desc(item.deploy_result), "created_at": item.created_at.strftime('%Y-%m-%d %H:%M:%S'),
              "created_by": item.creator_account, "wf_status": data_dicts.WfActivityConst.convert_to_desc(item.wf_status)}
        vos.append(vo)

    return jsonify({"total": pagination.total, "rows": vos})