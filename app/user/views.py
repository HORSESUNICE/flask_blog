from flask import render_template, request, redirect, url_for, abort, flash, current_app
from flask_login import login_required, current_user

from . import user
from .. import db
from ..main.forms import EditProfileForm, EditProfileAdminForm, PostForm
from ..models import User, Permission, Role, Post
from ..decorators import admin_required

@user.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(body=form.body.data, title=form.title.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user/index.html', form=form, posts=posts,
                           pagination=pagination)

@user.route('/<name>')
@login_required
def username(name):
    user = User.query.filter_by(name=name).first_or_404()
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user/user.html', user=user)

@user.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.realname = form.realname.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.username', name=current_user.name))
    form.realname.data = current_user.realname
    return render_template('user/edit_profile.html', form=form)


@user.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@admin_required
@login_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.name = form.name.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.realname = form.realname.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.username', name=user.name))
    form.email.data = user.email
    form.name.data = user.name
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.realname.data = user.realname
    return render_template('user/edit_profile.html', form=form)