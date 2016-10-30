#!usr/bin/env python
#coding=utf-8

from flask import render_template, redirect, url_for, session, current_app
from . import main
from .forms import NameForm
from ..models import User
from .. import db
from .. import email

@main.route('/', methods=['POST','GET'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter(User.username == form.username.data).first()
        if user is None:
            user = User(username = form.username.data)
            db.session.add(user)
            session['known'] = False
            if current_app.config['FLASK_ADMIN']:
                email.send_email(current_app.config['FLASK_ADMIN'], 'New User',
                                 'mail/new_user', user=user)
        else:
            session['known'] = True
        session['username'] = form.username.data
        return redirect(url_for('main.index'))
    return render_template('index.html', form = form,
                           username = session.get('username'),
                           known = session.get('known', False))
