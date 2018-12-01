from flask import Blueprint, render_template, abort, jsonify, request
from flask_login import login_required
from jinja2 import TemplateNotFound
from ..models import Host


host_view = Blueprint('host_view', __name__, template_folder='templates')


@host_view.route('/host/index')
@login_required
def index():
    try:
        return render_template('sys/hostlist.html')
    except TemplateNotFound:
        abort(404)


@host_view.route('/host/gethostlist')
@login_required
def get_host_list():
    limitstr = request.values.get("limit")
    offsetstr = request.values.get("offset")
    limit = 10
    if limitstr.strip():
        limit = int(limitstr)
    offset = 0
    if offsetstr.strip():
        offset = int(offsetstr)
    page = offset / limit + 1
    pagination = Host.Host.query.paginate(page, per_page=limit, error_out=False)
    hostitems = pagination.items
    hostVos = []
    for hostitem in hostitems:
        hostvo = {"host_id": hostitem.host_id, "internal_ip": hostitem.internal_ip, "external_ip": hostitem.external_ip, "host_name": hostitem.host_name}
        hostVos.append(hostvo)

    return jsonify({"total": pagination.total, "rows": hostVos})

