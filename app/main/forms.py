from flask_wtf import FlaskForm
from flask_pagedown.fields import PageDownField
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, Email
from ..models import User, Role

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

class EditProfileForm(FlaskForm):
    realname = StringField('Realname', validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(3, 24),
                                           Regexp('^[A-Za-z]*$', 0,
                                                  'Only English letters R allowed!')])
    realname = StringField('Realname', validators=[DataRequired(), Length(1, 64)])
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    role = SelectField('Role', coerce=int)
    confirmed = BooleanField('Confirmed')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_name(self, field):
        if field.data != self.user.name and \
                User.query.filter_by(name=field.data).first():
            raise ValidationError('Name already in use.')

class PostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(1,32)])
    body = PageDownField("想说点什么?", validators=[DataRequired()])
    submit = SubmitField('发布')

class CommentForm(FlaskForm):
    body = StringField('你对文章有什么想法?', validators=[DataRequired()])
    submit = SubmitField('发布')