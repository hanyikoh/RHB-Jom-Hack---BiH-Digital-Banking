from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from wtforms.widgets import TextArea
from app.models import User, Company

class LoginForm(FlaskForm):
    username = StringField(label='Username:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')

class RegisterForm(FlaskForm):
    username = StringField(label='Username:', validators=[DataRequired()])
    email = StringField(label='Email Address:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    confirm_password = PasswordField(label='Confirm Password:', validators=[EqualTo('password'), DataRequired()])
    register = SubmitField(label='Register')

    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a different username')

    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email Address already exists! Please try a different email address')    
    
class CompanyDetailForm(FlaskForm):
    companyName = StringField(label='Company Name:', validators=[DataRequired()])
    companyAddress1 = TextAreaField(label='Address Line 1:', validators=[DataRequired()])
    companyAddress2 = TextAreaField(label='Address Line 2:', validators=[DataRequired()])
    city = StringField(label='City/State', validators=[DataRequired()])
    zip = IntegerField(label='Zip Code:', validators=[DataRequired()])
    country = StringField(label='Country', validators=[DataRequired()])
    businessType = StringField(label='Type of Business', validators=[DataRequired()])
    contactNumber = StringField(label='Contact Number', validators=[DataRequired()])
    contactEmail = StringField(label='Contact Email', validators=[DataRequired()])
    website = StringField(label='Website (Optional)')

    introduction = TextAreaField(label='Introduce yourself and tell us something interesting about you?', validators=[DataRequired()])
    why = TextAreaField(label='Why do you do what you do?', validators=[DataRequired()])
    problems = TextAreaField(label='What problems are you solving?', validators=[DataRequired()])
    benefit = TextAreaField(label='Who specifically will benefit from this (ICA/ICP)?', validators=[DataRequired()])
    solving = TextAreaField(label='How are you solving this/their problems?', validators=[DataRequired()])
    
class StrategyForm(FlaskForm):
    valuePreposition = TextAreaField(label='What your value proposition is?', validators=[DataRequired()])
    customerRelationships = TextAreaField(label='How are you going to create and nurture customer relationships?', validators=[DataRequired()])
    startupAccess = TextAreaField(label='How will the customers be able to access your startup?', validators=[DataRequired()])

    partners = TextAreaField(label='Who are the partners that your startup will need to work with in order to get things working?', validators=[DataRequired()])
    valueGenerate = TextAreaField(label='What are the things that you need to do in order to generate things such as: your value proposition; distribution channels for your solution; customer relationships; revenue', validators=[DataRequired()])
    resources = TextAreaField(label='What are the specific resources you need to generate value?', validators=[DataRequired()])

    introduction = TextAreaField(label='Introduce yourself and tell us something interesting about you?', validators=[DataRequired()])
    why = TextAreaField(label='Why do you do what you do?', validators=[DataRequired()])
    problems = TextAreaField(label='What problems are you solving?', validators=[DataRequired()])
    benefit = TextAreaField(label='Who specifically will benefit from this (ICA/ICP)?', validators=[DataRequired()])
    solving = TextAreaField(label='How are you solving this/their problems?', validators=[DataRequired()])