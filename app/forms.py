from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User


#here we build classes for each from, using the WTForms plugin
#Each var represents a form field. These fields are classes from FlaskForm

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm): 
    #form fields from FlaskForm classes
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()]) #Email() = stock validation for email address format
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')]) #EqualTo() stock validation to check against password var
    submit = SubmitField('Register')

    #user input validation --------------------
    #When you add any methods that match the pattern 'validate_<field_name>', 
    #WTForms takes those as custom validators and invokes them in addition 
    #to the stock validators.

    def validate_username(self, username): #'Self' is like 'this' in js, i think. refers to the individual instance of the function being called(?)
        user= User.query.filter_by(username=username.data).first()
        if user is not None: #making sure that the query did not produce any results
            raise ValidationError('Please use a different username.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None: #making sure that the query did not produce any results
            raise ValidationError('This email address already exists')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
# The implementation is in a custom validation method, but there is an overloaded constructor that accepts the original username as an argument. 
# This username is saved as an instance variable, and checked in the validate_username() method. 
# If the username entered in the form is the same as the original username, then there is no reason to check the database for duplicates.
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', 
        validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')