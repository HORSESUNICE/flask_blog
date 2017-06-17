import os

from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

from app import create_app, db
from app.models import Game, User, Role, Gameaccount

app = create_app(os.environ.get('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, User=User, Game=Game, Role=Role, Gameaccount=Gameaccount)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

def account():
    from app import db
    from app.models import Game, User, Gameaccount, Role

    man1 = User.query.filter_by(name='man1').first()
    man2 = User.query.filter_by(name='man2').first()
    man3 = User.query.filter_by(name='man3').first()
    lol = Game.query.filter_by(name='LOL').first()

    acc1 = Gameaccount(account='7105',password='1974',user=man1,game=lol)
    acc2 = Gameaccount(account='711',password='5484',user=man1,game=lol)
    acc3 = Gameaccount(account='479',password='21257',user=man2,game=lol)
    acc4 = Gameaccount(account='78451',password='000',user=man3,game=lol)

    accountlist = [acc1, acc2, acc3, acc4]

    db.session.add_all(accountlist)
    db.session.commit()

@manager.command
def deploy():
    """Run deployment tasks."""
    from flask_migrate import upgrade
    upgrade()
    Role.insert_roles()
    Game.insert_games()
    User.insert_users()
    account()

if __name__ == '__main__':
    manager.run()