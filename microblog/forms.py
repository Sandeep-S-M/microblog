from flask_wtf import FlaskForm
from microblog import db
from microblog.models import User
import sqlalchemy as sa
from flask import request
from wtforms import StringField,PasswordField,BooleanField,SubmitField,TextAreaField
from wtforms.validators import DataRequired,Email,EqualTo,ValidationError,Length


class RegisterForm(FlaskForm):
  username = StringField('Username',validators=[DataRequired()])
  email = StringField('Email',validators=[Email(),DataRequired()])
  password = PasswordField('Password',validators=[DataRequired()])
  password2 = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
  submit = SubmitField('Register')
  
  def validate_username(self,username):
    user = db.session.scalar(sa.select(User).where(User.username == username.data))
    if user is not None:
      raise ValidationError('please try with another username ')
  def validate_email(self,email):
    mail = db.session.scalar(sa.select(User).where(User.email == email.data))
    if mail is not None:
      raise ValidationError('please try with another email ')
    

class LoginForm(FlaskForm):
  username = StringField('Username',validators=[DataRequired()])
  password = PasswordField('Password',validators=[DataRequired()])
  remember_me = BooleanField('remember me')
  submit = SubmitField('Sign In')
  
class EditProfileForm(FlaskForm):
  username = StringField('Username',validators=[DataRequired()])
  about_me = TextAreaField('Bio:',validators=[Length(min=0,max=140)])
  submit = SubmitField("Submit")
  def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username
  
  def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(User.username == username.data))
            if user is not None:
                raise ValidationError('Please use a different username.')
              
              
class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')
    
class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')
class SearchForm(FlaskForm):
    q = StringField(('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}
        super(SearchForm, self).__init__(*args, **kwargs)

class MessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[
        DataRequired(), Length(min=0, max=140)])
    submit = SubmitField('Submit')