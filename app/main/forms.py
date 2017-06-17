from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, Email
from ..models import User

class LoginForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(3,24)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Login In')

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(3,24),
                                           Regexp('^[A-Za-z]*$', 0,
                                                  'Only English letters R allowed!')])
    realname = StringField('Realname', validators=[DataRequired(), Length(1,64)])
    email = StringField('Email', validators=[DataRequired(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(6,24),
                                                     Regexp('^[A-Za-z0-9]*$', 0,
                                                            'Only English letters & numbers R allowed!'),
                                                     EqualTo('password2', message='Password must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_name(self, field):
        if User.query.filter_by(name=field.data).first():
            raise ValidationError('Name already in use.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already in use.')