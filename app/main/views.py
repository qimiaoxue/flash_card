from datetime import datetime
from datetime import timedelta
from flask import render_template
from flask import abort
from flask_login import current_user
from app.models import User
from app.models import Role
from app.models import Task
from flask import redirect
from flask import url_for
from flask import flash
from flask import request
from flask import current_app
from flask_login import login_required
from .. import db
from . import main
from app.decorators import admin_required
from app.main.forms import EditProfileForm
from app.main.forms import EditProfileAdminForm
from app.main.forms import PostForm
from ..models import Permission, Post

hours = [
    0.5,
    24,
    24 * 3,
    24 * 7,
    24 * 15,
    24 * 31,
    24 * 63,
]


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if (
        current_user.can(Permission.WRITE_ARTICLES) and
        form.validate_on_submit()
    ):
        post = Post(
            question=form.question.data,
            answer=form.answer.data,
            author=current_user._get_current_object())
        db.session.add(post)
        for hour in hours:
            task = Task(
                post=post,
                start_timestamp=datetime.utcnow() + timedelta(hours=hour)
            )
            db.session.add(task)

        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
                           pagination=pagination)


@main.route('/user/<username>', methods=['GET', 'POST'])
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', posts=[post])


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.question = form.question.data
        post.answer = form.answer.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.question.data = post.question
    form.answer.data = post.answer
    return render_template('edit_post.html', form=form)
