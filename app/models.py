from . import db

class Friend(db.Model):
    __tablename__ = 'friends'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    realname = db.Column(db.Unicode(64), unique=True)
    gameaccounts = db.relationship('Gameaccount', backref='friend', lazy='dynamic')

    def __repr__(self):
        return '<Friend %r>' % self.name

class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    gameaccounts = db.relationship('Gameaccount', backref='game', lazy='dynamic')

    def __repr__(self):
        return '<Game %r>' % self.name

class Gameaccount(db.Model):
    __tablename__ = 'gameaccounts'
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64), unique=False)
    name_id = db.Column(db.Integer, db.ForeignKey('friends.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))

    def __repr__(self):
        return '<Gameaccount %r>' % self.id