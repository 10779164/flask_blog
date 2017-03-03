#! usr/bin/env python
#coding=utf-8

from flask_wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField, ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp

from ..models import Role, User


class EditProfileForm(Form):
    '''普通用户级别的资料编辑表单'''
    name = StringField(u'真实名字', validators=[Length(0, 50)])
    location = StringField(u'地址', validators=[Length(0, 50)])
    about_me = TextAreaField(u'自我介绍')
    submit = SubmitField(u'提交')

class EditProfileAdminForm(Form):
    '''管理员级别的资料编辑'''
    email = StringField(u'邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(u'用户名', validators=[DataRequired(), Length(1, 64),
                                               Regexp(ur'^[\u4e00-\u9fa5a-zA-Z][\u4e00-\u9fa5_@\-a-zA-Z0-9]+$',
                                                      0, u'用户名只能以中文或字母开头，不能为空')])
    confirmed = BooleanField(u'认证')
    role = SelectField(u'角色', coerce= int)
    name = StringField(u'真实名字', validators=[Length(0, 50)])
    location = StringField(u'地址', validators=[Length(0, 50)])
    about_me = TextAreaField(u'自我介绍')
    submit = SubmitField(u'提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter(User.email == field.data).first():
            raise ValidationError(u'该邮箱已被注册')

    def validate_user(self, field):
        if field.data != self.user.username and User.query.filter(User.username == field.data).first():
            raise ValidationError(u'该用户名已被注册')

class PostForm(Form):
    '''博客文章'''
    body = TextAreaField(u'写下你的想法', validators=[DataRequired()])
    submit = SubmitField(u'提交')