# coding=utf-8

from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from datetime import datetime
import time
import hashlib

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy = 'dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT|
                     Permission.WRITE_ARTICLES, 1),
            'Moderator' : (Permission.FOLLOW |
                     Permission.COMMENT|
                     Permission.WRITE_ARTICLES |
                           Permission.MODERATE_COMMENTS, 0),
            'Adminitrators' : (0xff, 0)
        }
        for r in roles:
            role = Role.query.filter(Role.name == r).first()
            if role is None:
                role = Role(name = r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


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

    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    avatar_hash = db.Column(db.String(32))

    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASK_ADMIN']:
                self.role = Role.query.filter(Role.permissions == 0xff).first()
            if self.role is None:
                self.role = Role.query.filter(Role.default == True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5('747106549@qq.com'.encode('utf-8')).hexdigest()

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

    def can(self, permissions):
        '''进行位与操作，检验请求与赋予的角色'''
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_adminitrator(self):
        '''判断是否为管理员角色'''
        return self.can(Permission.ADMINISTER)

    def ping(self):
        '''刷新用户最后访问时间'''
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        '''通过gravatar网站加载邮箱头像'''
        if request.is_secure:
            url = 'https://secure/gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5('747106549@qq.com'.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}%d={default}%r={rating}'.format(
            url = url, hash = hash, size = size, default = default, rating = rating)

    @staticmethod
    def generate_fake(count=100):
        '''创建博客文章模拟数据'''
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True)
                     )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return '<User %r>' % self.username

# 加载用户的回调函数：接收Unicode字符串形式的用户标识符，如果有该用户就返回用户的对象，否则为None
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

class AnonymousUser(AnonymousUserMixin):
    '''此类为用户未登陆时的角色，保持一致性不用检验用户是否已登陆，
     能自由调用current_user.can 和 current_user.is_administrator方法'''
    def can(self, permissions):
        return False

    def is_adminitrator(self):
        return False

#将Flask_Login中的AnonymousUserMixin类变成该AnonymousUser类
login_manager.anonymous_user = AnonymousUser

class Post(db.Model):
    '''博客文章'''
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp =  db.Column(db.DateTime, default= datetime.utcnow, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def generate_fake(count=100):
        '''生产虚拟博客文章'''
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count-1)).first()
            p = Post(
                body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                timestamp=forgery_py.date.date(True),
                author=u)
            db.session.add(p)
            db.session.commit()
