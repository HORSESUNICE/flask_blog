from . import db, login_manager

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            else:
                self.role = Role.query.filter_by(default=True).first()

    def __repr__(self):
        return '<User %r>' % self.name

    @property
    def password(self):
        raise AttributeError('password is hiden')

    @password.setter
    def password(self, password):
        self._password_hash = generate_password_hash(password)

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

    @staticmethod
    def insert_users():
        role1 = Role.query.filter_by(name='Administrator').first()
        role2 = Role.query.filter_by(name='Friend').first()
        users = {
            'admin': ('epsilon',
                     role1,
                     'admin',
                     'admin@qq.com'),
            'man1': ('m1',
                     role2,
                     'man1',
                     'm1@163.com'),
            'man2': ('m2',
                     role2,
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

class Gameaccount(db.Model):
    __tablename__ = 'gameaccounts'
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64), unique=False)
    name_id = db.Column(db.Integer, db.ForeignKey('users.id'))
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
