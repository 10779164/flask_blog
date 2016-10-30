#! usr/bin/env python
#coding=utf-8

from . import main
from flask import render_template

# 要想注册程序全局的错误处理，必须要用app_errorhandler
@main.app_errorhandler(404)
def page_not_found(e):
    render_template('404.html'), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    render_template('500.html'), 500