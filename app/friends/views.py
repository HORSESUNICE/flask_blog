from flask import render_template, session, redirect, url_for, abort

from datetime import datetime

from . import fd
from ..main.forms import NameForm
from ..models import Friend
from ..emails import send_email

@fd.route('/', methods=['GET', 'POST'])
def friends():
    form = NameForm()
    if form.validate_on_submit():
        friend = Friend.query.filter_by(name=form.name.data).first()
        if friend:
            session['name'] = friend.name
            session['realname'] = friend.realname
            session['pre'] = friend.name
            return redirect(url_for('.friend', name=session['name']))
        else:
            abort(403)
    return render_template('friends.html', form=form)

@fd.route('/<name>')
def friend(name):
    pre = session.get('pre', None)
    if name == pre:
        friend = Friend.query.filter_by(name=name).first()
        accounts = friend.gameaccounts.all()
        # begin = datetime.now()
        # send_email(' Welcome', 'welcome', 'yourqq@qq.com', 'your163@163.com', name=session['realname'], accounts=accounts)
        # end = datetime.now()
        # print(end-begin)
        return render_template('welcome.html', name=session['realname'], accounts=accounts)
    else:
        abort(403)