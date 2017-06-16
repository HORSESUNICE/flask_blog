import os

from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

from app import create_app, db
from app.models import Game, Friend, Gameaccount

app = create_app(os.environ.get('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, Friend=Friend, Game=Game, Gameaccount=Gameaccount)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

def account():
    from hello import db, Game, Friend, Gameaccount
    # db.create_all()
    lol = Game(name='LOL')
    battle = Game(name='BATTLE')
    mhxy = Game(name='XYQ')

    man1 = Friend(name='m1',realname='man1')
    man2 = Friend(name='m2',realname='man2')
    man3 = Friend(name='m3',realname='man3')
    man4 = Friend(name='m4', realname='man5')
    man5 = Friend(name='m5', realname='man5')
    man6 = Friend(name='m6', realname='man6')

    acc1 = Gameaccount(account='7105',password='1974',friend=man1,game=lol)
    acc2 = Gameaccount(account='711',password='5484',friend=man1,game=lol)
    acc3 = Gameaccount(account='479',password='21257',friend=man2,game=lol)
    acc4 = Gameaccount(account='78451',password='000',friend=man3,game=lol)

    gamelist = [lol, battle]
    friendlist = [man1, man2, man3, man4, man5, man6]
    accountlist = [acc1, acc2, acc3, acc4]
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

if __name__ == '__main__':
    manager.run()