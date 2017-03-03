#!/usr/bin/env python
# coding=utf-8

from flask import render_template, redirect, url_for, Blueprint, flash, request
from ..models import User, db, Role, Permission, Post
from ..decorators import admin_required
from flask_login import login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm, PostForm


main = Blueprint('main', __name__)


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


@main.route('/', methods=['POST', 'GET'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        # _get_current_object()为真正的用户对象
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('main.index'))
    # posts = Post.query.order_by(Post.timestamp.desc()).all()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=20, error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts, pagination=pagination)


@main.route('/user/<username>', methods=['POST', 'GET'])
def user(username):
    u = User.query.filter(User.username == username).first()
    posts = u.posts.order_by(Post.timestamp.desc()).all()
    return render_template('auth/user_info.html', user=u, posts=posts)


@main.route('/edit-profile', methods=['POST', 'GET'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash(u'编辑成功')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('auth/edit_info.html', form = form)


@main.route('/edit-profile/<int:uid>', methods=['POST', 'GET'])
@login_required
@admin_required
def edit_profile_admin(uid):
    u = User.query.get_or_404(uid)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        u.email = form.email.data
        u.username = form.username.data
        u.confirmed = form.confirmed.data
        u.role = Role.query.get(form.role.data)
        u.name = form.name.data
        u.location = form.location.data
        u.about_me = form.about_me.data
        db.session.add(u)
        return redirect(url_for('.user', username=u.username))
    form.email.data = u.email
    form.username.data = u.username
    form.confirmed.data = u.confirmed
    form.role.data = u.role_id
    form.name.data = u.name
    form.location.data = u.location
    form.about_me.data = u.about_me
    return render_template('auth/edit_info.html', form=form, user=u)
