#!usr/bin/env python
#coding=utf-8

from . import mail
from threading import Thread
from flask import current_app, render_template
from flask_mail import Message

def send_async(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['EMAIL_SUBJECT']+' '+subject, [to], sender = app.config['FLASK_MAIL_SENDER'] )
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async, args=[app, msg])
    thr.start()
    return thr