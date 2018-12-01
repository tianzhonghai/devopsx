from flask import Blueprint, render_template, redirect,session,request,abort


global_view = Blueprint('global_view',__name__)


@global_view.app_errorhandler(404)
def error(e):
    return render_template('error.html', e=e)


@global_view.app_errorhandler(500)
def error(e):
    return render_template('error.html', e=e)


@global_view.app_errorhandler(403)
def error(e):
    return render_template('noauth.html', e=e)
