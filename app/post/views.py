from flask import render_template, abort, flash, redirect, url_for
from . import post
from ..models import Post, Permission
from .. import db
from flask_login import login_required, current_user
from ..main.forms import PostForm

@post.route('/<int:id>')
def article(id):
    post = Post.query.get_or_404(id)
    return render_template('post/post.html', posts=[post])

@post.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.article', id=post.id))
    form.body.data = post.body
    form.title.data = post.title
    return render_template('post/edit_post.html', form=form)