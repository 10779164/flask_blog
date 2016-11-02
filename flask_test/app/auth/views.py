#!usr/bin/env python
# coding=utf-8

from flask import render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, login_required, logout_user, current_user
from . import auth
from ..models import User
from .forms import LoginForm, RegistrationForm, AlterPswForm
from .. import db
from ..email import send_email

@auth.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.email == form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            session['username'] = user.username
            session['uid'] = user.id
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(u'用户名错误或密码错误！请重新输入')
    return render_template('auth/login.html', form = form)

@auth.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    flash(u'%s用户已经退出账号！'% session['username'])
    return  redirect(url_for('auth.login'))

@auth.route('/register', methods=['POST', 'GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(current_app.config['FLASK_MAIL_SENDER'], 'Confirm Your Account',
                   'auth/email/confirm', user = user, token = token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form = form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    '''邮箱确认路由'''
    if current_user.confirmed == 1:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account, Thanks')
    else:
        flash('The confirmation link is invalid or has expired!!')
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    '''处理程序中过滤未确认的用户'''
    if current_user.is_authenticated and current_user.confirmed == 0 \
        and request.endpoint[:5] != 'auth.' and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    ''''''
    if current_user.is_anonymous or current_user.confirmed == 1:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_app.config['FLASK_MAIL_SENDER'], 'Confirm Your Account',
                   'auth/email/confirm', user = current_user, token = token)
    flash('A new confirmation email has been sent to you by email')
    return redirect(url_for('main.index'))

@auth.route('/user_info', methods=['POST', 'GET'])
@login_required
def get_user_info():
    '''用户信息'''
    if current_user.confirmed == 0:
        redirect(url_for('auth.before_request'))

    return render_template('auth/user_info.html')

@auth.route('/alter_psw', methods=['POST', 'GET'])
@login_required
def alter_psw():
    form = AlterPswForm()
    if form.validate_on_submit():
        user = User.query.get(session['uid'])
        if user and user.verify_password(form.old_password.data):
            user.password = form.password.data
            db.session.commit()
            flash(u'密码修改成功')
            logout_user()
            return redirect(url_for('auth.login'))
        else:
            flash(u'密码错误')
            return redirect(url_for('auth.alter_psw'))

    return render_template('auth/alter_psw.html', form = form)