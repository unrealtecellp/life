from flask_wtf import FlaskForm
from wtforms import (StringField,
                        SubmitField,
                        TextAreaField,
                        SelectField,
                        PasswordField,
                        RadioField
                    )
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
    position = SelectField(label='Position', validators=[DataRequired()], choices=[('student', 'Student'), ('researchScholar', 'Research Scholar'), ('professor', 'Professor'), ('associateProfessor', 'Associate Professor'), ('assistantProfessor', 'Assistant Professor'), ('industryProfessional', 'Industry Professional')], render_kw={'placeholder': 'position'})
    organisation_name = StringField(label='Organisation Name', validators=[DataRequired()], render_kw={'placeholder': 'organisation name'})
    organisation_type = SelectField(label='Organisation Type', validators=[DataRequired()], choices=[('academiaResearchUniversity', 'Academia/Research/University'), ('startup', 'Startup'), ('industry', 'Industry'), ('other', 'Other')], render_kw={'placeholder': 'organisation type'})
    country = StringField(validators=[DataRequired()], render_kw={'placeholder': 'country'})
    city = StringField(validators=[DataRequired()], render_kw={'placeholder': 'city'})
    email = StringField(validators=[DataRequired()], render_kw={'placeholder': 'email'})
    languages = StringField(validators=[DataRequired()], render_kw={'placeholder': 'languages'})
    memory_requirement = RadioField(label='Memory Requirement', validators=[DataRequired()], choices=[('upto100Mb', 'upto 100Mb'), ('upto200Mb', 'upto 200Mb'), ('upto500Mb', 'upto 500Mb'), ('upto1Gb', 'upto 1Gb'), ('greaterThan1Gb', '> 1 Gb')], render_kw={'id': 'memory_requirement'})
    app_use_reason = TextAreaField(validators=[DataRequired()], description='How you plan to use this app (Please specify clearly as this information will be crucial for creating your account)', render_kw={'placeholder': 'App Use Reason'})
    submit = SubmitField('Add User')

    def validate_username(self, username):
        user = userlogin.find_one({'username': username.data})
        # UserLogin(userlogin.find_one({'username': username.data})["username"])
        if user is not None:
            raise ValidationError('Please use a different username.')