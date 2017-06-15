from flask import Flask,render_template, session, redirect, url_for, abort
from flask_script import Manager, Shell
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand

from datetime import datetime

# web form
class NameForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login In')

app = Flask(__name__)

# config
app.config['SECRET_KEY'] = 'any epsilon is greater than 0'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'mysql+pymysql://root:password@localhost/flask_blog'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# advanced
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Friend(db.Model):
    __tablename__ = 'friends'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    realname = db.Column(db.Unicode(64), unique=True)
    # nickname = db.Column(db.Unicode(64), unique=True)
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

def make_shell_context():
    return dict(app=app, db=db, Friend=Friend, Game=Game, Gameaccount=Gameaccount)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

def account():
    from hello import db, Game, Friend, Gameaccount
    # db.create_all()
    lol = Game(name='LOL')
    battle = Game(name='BATTLE')
    man1 = Friend(name='m1',realname='man1')
    man2 = Friend(name='m2',realname='man2')
    man3 = Friend(name='m3',realname='man3')
    acc1 = Gameaccount(account='7105',password='1974',friend=man1,game=lol)
    acc2 = Gameaccount(account='711',password='5484',friend=man1,game=lol)
    acc3 = Gameaccount(account='479',password='21257',friend=man2,game=lol)
    acc4 = Gameaccount(account='78451',password='000',friend=man3,game=lol)
    acc5 = Gameaccount(account='222',password='000',friend=man3,game=battle)
    gamelist = [lol, battle]
    friendlist = [man1, man2, man3]
    accountlist = [acc1, acc2, acc3, acc4, acc5]
    db.session.add_all(gamelist)
    db.session.add_all(friendlist)
    db.session.add_all(accountlist)
    db.session.commit()

@manager.command
def deploy():
    """Run deployment tasks."""
    from flask_migrate import upgrade
    upgrade()
    account()

@app.route('/')
def index():
    return render_template('base.html')

@app.errorhandler(403)
def page_not_found(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html',
                           current_time=datetime.utcnow()), 500

@app.route('/friends', methods=['GET', 'POST'])
def friends():
    form = NameForm()
    if form.validate_on_submit():
        friend = Friend.query.filter_by(name=form.name.data).first()
        if friend:
            session['name'] = friend.name
            session['realname'] = friend.realname
            session['pre'] = friend.name
            return redirect(url_for('friend', name=session['name']))
        else:
            abort(403)
    return render_template('friends.html', form=form)

@app.route('/friends/<name>')
def friend(name):
    pre = session.get('pre', None)
    if name == pre:
        friend = Friend.query.filter_by(name=name).first()
        accounts = friend.gameaccounts.all()
        return render_template('welcome.html', name=session['realname'], accounts=accounts)
    else:
        abort(403)


if __name__ == '__main__':
    manager.run()

