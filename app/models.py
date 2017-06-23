from . import db, login_manager

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime

from flask import current_app, url_for
from app.exceptions import ValidationError
from flask_login import UserMixin, AnonymousUserMixin
from markdown import markdown
import bleach

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    FRIEND = 0x10
    ADMINISTER = 0x80

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Friend': (Permission.FOLLOW |
                       Permission.COMMENT |
                       Permission.WRITE_ARTICLES |
                       Permission.MODERATE_COMMENTS |
                       Permission.FRIEND, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    gameaccounts = db.relationship('Gameaccount', backref='game', lazy='dynamic')

    @staticmethod
    def insert_games():
        games = {
            'LOL',
            'BATTLE',
            'XYQ'
        }
        for g in games:
            game = Game.query.filter_by(name=g).first()
            if game is None:
                game = Game(name=g)
                db.session.add(game)
        db.session.commit()

    def __repr__(self):
        return '<Game %r>' % self.name

class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True, index=True)
    _password_hash = db.Column(db.String(128))
    realname = db.Column(db.Unicode(64), unique=False)
    gameaccounts = db.relationship('Gameaccount', backref='user', lazy='dynamic')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            else:
                self.role = Role.query.filter_by(default=True).first()
        self.follow(self)

    def __repr__(self):
        return '<User %r>' % self.name

    @property
    def password(self):
        raise AttributeError('password is hiden')

    @password.setter
    def password(self, password):
        self._password_hash = generate_password_hash(password)

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
            .filter(Follow.follower_id == self.id)

    def verify_password(self, password):
        return check_password_hash(self._password_hash, password)

    def generate_confirmation_token(self, expiration=900):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def is_friend(self):
        return self.can(Permission.FRIEND)

    @staticmethod
    def insert_users():
        role1 = Role.query.filter_by(name='Administrator').first()
        role2 = Role.query.filter_by(name='Friend').first()
        role3 = Role.query.filter_by(name='User').first()
        users = {
            'admin': ('epsilon',
                     role1,
                     'admin',
                     'email1@qq.com'),
            'firstman': ('man1',
                         role2,
                         'man1',
                         'email2@163.com'),
            'secondman': ('man2',
                          role3,
                          'man2',
                          None),
            'man3': ('m3',
                     role2,
                     'man3',
                     None),
            'man4': ('m4',
                     role2,
                     'man4',
                     None),
        }
        for u in users:
            user = User.query.filter_by(name=u).first()
            if user is None:
                user = User(name=u)
            user.realname = users[u][0]
            user.role = users[u][1]
            user.password = users[u][2]
            if users[u][3]:
                user.email = users[u][3]
            db.session.add(user)
        db.session.commit()

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     name=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     realname=forgery_py.name.full_name())
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
            .filter(Follow.follower_id == self.id)

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def to_json(self):
        json_user = {
            'url': url_for('api_1_0.get_user', id=self.id, _external=True),
            'username': self.name,
            'posts': url_for('api_1_0.get_user_posts', id=self.id, _external=True),
            'followed_posts': url_for('api_1_0.get_user_followed_posts',
                                      id=self.id, _external=True),
            'post_count': self.posts.count()
        }
        return json_user

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32))
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
                     timestamp=forgery_py.date.date(True),
                     title=forgery_py.lorem_ipsum.title(randint(1,2)),
                     author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_post = {
            'url': url_for('api_1_0.get_post', id=self.id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api_1_0.get_user', id=self.author_id,
                              _external=True),
            'comments': url_for('api_1_0.get_post_comments', id=self.id,
                                _external=True),
            'comment_count': self.comments.count()
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        title = json_post.get('title',None)
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        return Post(body=body, title=title)

db.event.listen(Post.body, 'set', Post.on_changed_body)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_comment = {
            'url': url_for('api_1_0.get_comment', id=self.id, _external=True),
            'post': url_for('api_1_0.get_post', id=self.post_id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api_1_0.get_user', id=self.author_id,
                              _external=True),
        }
        return json_comment

    @staticmethod
    def from_json(json_comment):
        body = json_comment.get('body')
        if body is None or body == '':
            raise ValidationError('comment does not have a body')
        return Comment(body=body)

db.event.listen(Comment.body, 'set', Comment.on_changed_body)

class Gameaccount(db.Model):
    __tablename__ = 'gameaccounts'
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64), unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))

    def __repr__(self):
        return '<Gameaccount %r>' % self.id

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser
