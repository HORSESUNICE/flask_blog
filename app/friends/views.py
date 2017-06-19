from flask import render_template, session, redirect, url_for, abort
from flask_login import login_required

from datetime import datetime

from . import fd
from ..main.forms import LoginForm
from ..models import User, Permission
from ..emails import send_email
from ..decorators import permission_required

# @fd.route('/', methods=['GET', 'POST'])
# @permission_required(Permission.FRIEND)
# @login_required
# def friends():
#     form = LoginForm()
#     if form.validate_on_submit():
#         friend = User.query.filter_by(name=form.name.data).first()
#         if friend:
#             session['name'] = friend.name
#             session['realname'] = friend.realname
#             session['pre'] = friend.name
#             return redirect(url_for('.friend', name=session['name']))
#         else:
#             abort(403)
#     return render_template('friends.html', form=form)

@fd.route('/<name>')
@permission_required(Permission.FRIEND)
@login_required
def friend(name):
    friend = User.query.filter_by(name=name).first()
    if friend:
        accounts = friend.gameaccounts.all()
        return render_template('welcome.html', name=friend.realname, accounts=accounts)
    else:
        abort(404)