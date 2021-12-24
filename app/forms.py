from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, PasswordField, SelectField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from app import mongo
from app.models import UserLogin


userlogin = mongo.db.userlogin                          # collection of users and their login details

# user login form
class UserLoginForm(FlaskForm):
    username = StringField(validators=[DataRequired()], render_kw={'placeholder': 'username'})
    password = PasswordField(validators=[DataRequired()], render_kw={'placeholder': 'password'})
    submit = SubmitField('Login')


# new user registration form
class RegistrationForm(FlaskForm):
    username = StringField(validators=[DataRequired()], render_kw={'placeholder': 'username'})
    password = PasswordField(validators=[DataRequired()], render_kw={'placeholder': 'password'})
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')], \
                render_kw={'placeholder': 'confirm password'})
    submit = SubmitField('Add User')

    def validate_username(self, username):
        user = userlogin.find_one({'username': username.data})
        # UserLogin(userlogin.find_one({'username': username.data})["username"])
        if user is not None:
            raise ValidationError('Please use a different username.')