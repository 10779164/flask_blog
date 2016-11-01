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
    return render_template('index.html')
