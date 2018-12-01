from flask import (Blueprint, render_template, abort, request, redirect, url_for, flash)
from jinja2 import TemplateNotFound
from .. import login_manager
from ..models import User
from flask_login import login_user, logout_user
import hashlib


home_view = Blueprint('home_view', __name__)


@home_view.route("/")
def index():
    try:
        return render_template('home/index.html')
    except TemplateNotFound:
        abort(404)


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
