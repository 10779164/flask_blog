#!usr/bin/env python
#coding=utf-8

from flask import render_template, redirect, url_for, session, current_app, abort, flash
from . import main
from ..models import User, db, Role, Permission, Post
from ..decorators import admin_required
from flask_login import login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm, PostForm

@main.route('/', methods=['POST','GET'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        # _get_current_object()为真正的用户对象
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('main.index'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', form=form, posts=posts)

@main.route('/user/<username>', methods=['POST', 'GET'])
def user(username):
    user = User.query.filter(User.username == username).first()
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('auth/user_info.html', user = user, posts = posts)

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
        return redirect(url_for('.user', username = current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('auth/edit_info.html', form = form)

@main.route('/edit-profile/<int:id>', methods=['POST', 'GET'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user = user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        return redirect(url_for('.user', username = user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('auth/edit_info.html', form = form, user = user)
