#! usr/bin/env python
#coding=utf-8

from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class NameForm(Form):
    username = StringField('what is your name?', validators=[DataRequired()])
    submit = SubmitField('submit')