#forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone (Optional)', validators=[Optional()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    profile_pic = FileField('Profile Picture (Optional)', validators=[Optional()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class BookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image_file = FileField('Book Cover Image', validators=[Optional()])
    submit = SubmitField('Add Book')

class CommentForm(FlaskForm):
    content = TextAreaField('Add a Comment', validators=[DataRequired()])
    submit = SubmitField('Post Comment')

class AddressForm(FlaskForm):
    address = TextAreaField('Shipping Address', validators=[DataRequired()])
    submit = SubmitField('Save Address')