from flask import Flask,render_template, session, redirect, url_for
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo

from datetime import datetime


# web form

class NameForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login In')

# app
app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

app.config['SECRET_KEY'] = 'any epsilon is greater than 0'

@app.route('/')
def index():
    return render_template('base.html')

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
        session['name'] = form.name.data
        session['password'] = form.password.data
        return redirect(url_for('friend', name=session['name']))
    return render_template('friends.html', form=form)

@app.route('/friends/<name>')
def friend(name):
    return render_template('welcome.html', name=name)


if __name__ == '__main__':
    manager.run()