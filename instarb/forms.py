from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, SubmitField, BooleanField, PasswordField, TextAreaField, RadioField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from instarb.models import User, UserInstagramAccounts

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registerd. Please login to continue')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture',validators=[FileAllowed(['jpg','png','jpeg'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if current_user.username != username.data:
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError('Username already taken. Please choose a different one')

    def validate_email(self, email):
        if current_user.email != email.data:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already registerd. Please login to continue')


class AccountUsers(FlaskForm):
    name = StringField('Name',validators=[DataRequired()])
    username = StringField('Instagram Username', validators=[DataRequired()])
    password = PasswordField('Instagram Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Instagram Password', validators=[DataRequired(), EqualTo('password')])
    profile_pic = FileField('Upload Instagram profile picture', validators=[FileAllowed(['jpg','png','jpeg'])])
    submit = SubmitField('Add Account')

    def validate_username(self, username):
        insta = UserInstagramAccounts.query.filter_by(insta_username=username.data).first()
        if insta:
            raise ValidationError('Username already exits in our database. Please enter a different one. If you want to update password please visit Users tab')


class UpdateInstagramAccountForm(FlaskForm):
    username = StringField('Username',validators=[])
    password = PasswordField('Password',validators=[])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password')])
    profile_pic = FileField('Update Instagram profile picture', validators=[FileAllowed(['jpg','png','jpeg'])])
    submit = SubmitField('Update')

class AutoLikerForm(FlaskForm):
    title = StringField('Task Name', validators=[DataRequired()])
    list_of_urls = TextAreaField('List of URLs', validators=[DataRequired()])
    insta_account=RadioField('Choose one Instagram account to run Auto Liker', choices=[], validators=[DataRequired()], coerce=int)
    submit = SubmitField('Run')

    def validate_insta_account(self, insta_account):
        if insta_account:
            pass
        else:
            raise ValidationError('Select your Instagram account')

class SettingsForm(FlaskForm):
    live_browser=SelectField('Live Browser', choices=[('True','Enable'),('False','Disable')])    
    do_like = SelectField('Enable/Disable Like', choices=[('True','Enable'),('False','Disable')])
    like_randomize = SelectField('Randomize Like', choices=[('True','Enable'),('False','Disable')])
    like_percentage = IntegerField('Percentage of URLs to like', validators=[NumberRange(min=0, max=100)])
    submit = SubmitField('Save')



    
   
