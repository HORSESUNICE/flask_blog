from flask import render_template, redirect, url_for, abort, flash, request

from flask_login import login_user, logout_user, login_required, current_user

from . import auth
from ..main.forms import LoginForm, RegistrationForm
from ..models import User
from .. import db
from ..emails import send_confirm_email

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            if user.is_friend():
                return redirect(url_for('fd.friend', name=current_user.name))
            else:
                return redirect(url_for('user.mainpage', name=current_user.name))
        else:
            flash('Invalid user or password.')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data,
                    realname=form.realname.data,
                    email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_confirm_email('email', user.email, user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_confirm_email('email', current_user.email, user=current_user, token=token)
    flash('A confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))