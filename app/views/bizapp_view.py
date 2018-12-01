from flask import Blueprint, render_template, abort, jsonify, request
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from ..models import BizApp


bizapp_view = Blueprint('bizapp_view', __name__, template_folder='templates')


@bizapp_view.route('/bizapp/index')
@login_required
def index():
    try:
        return render_template('sys/bizapplist.html')
    except TemplateNotFound:
        abort(404)


@bizapp_view.route('/host/getbizapplist')
@login_required
def get_bizapp_list():
    limitstr = request.values.get("limit")
    offsetstr = request.values.get("offset")
    limit = 10
    if limitstr.strip():
        limit = int(limitstr)
    offset = 0
    if offsetstr.strip():
        offset = int(offsetstr)
    page = offset / limit + 1
    pagination = BizApp.BizApp.query.paginate(page, per_page=limit, error_out=False)
    items = pagination.items
    vos = []
    for item in items:
        vo = {"app_id": item.app_id, "app_name": item.app_name, "owner_phone": item.owner_phone, "owner_id": item.owner_id, "internal_ips": item.internal_ips}
        vos.append(vo)

    return jsonify({"total": pagination.total, "rows": vos})


@bizapp_view.route("/bizapp/searchmyapplistpage")
@login_required
def search_my_app_list_page():
    current_user_id = current_user.userid
    page = request.values.get('page')
    term = request.values.get('search', default="")
    limit = 10
    if term != "":
        pagination = BizApp.BizApp.query.filter(BizApp.BizApp.dev_id == current_user_id, BizApp.BizApp.app_id.like(term + '%')).paginate(page, per_page=limit, error_out=False)
    else:
        pagination = BizApp.BizApp.query.filter(BizApp.BizApp.dev_id == current_user_id).paginate(page, per_page=limit, error_out=False)

    items = pagination.items

    vos = []
    for item in items:
        vo = {"id": item.app_id, "text": item.app_id}
        vos.append(vo)

    return jsonify({"total": pagination.total, "results": vos})