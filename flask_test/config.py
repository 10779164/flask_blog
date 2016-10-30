#! usr/bin/env python
#coding=utf-8

import os

class Config:
    SECRET_KEY = os.getenv('SECRET-KEY') or 'n\x87\xac\xfbW\xe5Yc\xf1\xacs\xf3\xd1\xcd\xd3\xe0>\xa1\xbc\xee\xde\x9b$\xed'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    EMAIL_SUBJECT = 'flask_test example'
    FLASK_MAIL_SENDER = 'cyaoda222@163.com'
    # 电子邮件的收件人
    FLASK_ADMIN = 'cyaoda222@163.com'

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root@127.0.0.1/data_dev'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root@127.0.0.1/data_test'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root@127.0.0.1/data'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production' : ProductionConfig,
    'default' : DevelopmentConfig
}