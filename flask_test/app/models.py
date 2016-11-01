#! usr/bin/env python
# coding=utf-8

from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy = 'dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True, index=True)
    confirmed = db.Column(db.Integer, default = 0)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        '''生成hash密码'''
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        '''检验密码'''
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration = 3600):
        '''生成一个令牌'''
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        '''检验令牌'''
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = 1
        db.session.add(self)
        return True

    def __repr__(self):
        return '<User %r>' % self.username

# 加载用户的回调函数：接收Unicode字符串形式的用户标识符，如果有该用户就返回用户的对象，否则为None
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))