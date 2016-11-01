#!usr/bin/env python
# coding=utf-8

from flask_wtf import Form
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo
from ..models import User

class LoginForm(Form):
    '''登陆表单'''
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('password', validators=[DataRequired(), Length(6, 120)])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

class RegistrationForm(Form):
    email = StringField(u'邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(u'用户名', validators=[DataRequired(), Length(1, 64),
                                                   Regexp(ur'^[\u4e00-\u9fa5a-zA-Z][\u4e00-\u9fa5_@\-a-zA-Z0-9]+$',
                                                          0, u'用户名只能以中文或字母开头，不能为空')])
    password = PasswordField(u'密码', validators=[DataRequired(), EqualTo('password2', message=u'确认密码有误')])
    password2 = PasswordField(u'确认密码', validators=[DataRequired()])
    submit = SubmitField(u'提交')

    def validate_email(self, field):
        '''检验邮箱是否已注册'''
        if User.query.filter(User.email == field.data).first():
            raise ValidationError(u'该邮箱已被注册')

    def validate_username(self, field):
        '''检验用户名是否被注册'''
        if User.query.filter(User.username == field.data).first():
            raise ValidationError(u'该用户名已被注册')