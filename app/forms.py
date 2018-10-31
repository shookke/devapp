from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User, Container
from app import app

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    admin = BooleanField('Administrator')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    token = StringField('API Token', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class ContainerForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired()])
    database = StringField('Database Name', validators=[DataRequired()])
    db_user = StringField('Database User', validators=[DataRequired()])
    db_pw = PasswordField('Database Password', validators=[DataRequired()])
    prefix = StringField('Table Prefix')
    url = StringField('Domain Url', validators=[DataRequired()])
    submit = SubmitField('Create')

    def validate_name(self, name):
        container = Container.query.filter_by(name=name.data).first()
        if container is not None:
            raise ValidationError('Container with that name already exists')

    def validate_url(self, url):
        container = Container.query.filter_by(url=url.data).first()
        if container is not None:
            raise ValidationError('Container with that URL already exists.')

class EditContainerForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired()])
    url = StringField('Domain Url', validators=[DataRequired()])
    status = SelectField('Status', choices=[('SUCCESS', 'Up'), ('DOWN', 'Down'), ('None', 'New')], validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, original_name, *args, **kwargs):
        super(EditContainerForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if name.data != self.original_name:
            container = Container.query.filter_by(name=self.name.data).first()
            if container is not None:
                raise ValidationError('A container with that name already exists.')

class UploadForm(FlaskForm):
    sql = FileField('SQL File', validators=[FileRequired()])
    submit = SubmitField('Upload')
