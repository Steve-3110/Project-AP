from datetime import datetime as dt
from flask import *
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *

# Create the Task class
class Task:
    def __init__(self, name: str, priority: int, duration: int, predecessor: str, resources: str, user_name: str, time=None):
        self.name = name
        self.priority = priority
        self.duration = duration
        self.predecessor = predecessor
        self.resources = resources
        self.user_name = user_name
        self.time = time if time is not None else dt.now().strftime('%Y-%m-%d %H:%M')


# Create the class RegistrationForm
class RegistrationForm(FlaskForm):
    user_name = StringField('User Name', validators=[InputRequired()])
    email = StringField('E-mail', validators=[InputRequired()])
    family_name = StringField('Family Name', validators=[InputRequired()])
    surname = StringField('Surname', validators=[InputRequired()])
    dob = DateField('Date of Birth', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
        InputRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')


# Create the User class
class User:
    def __init__(self, Family_name, Date_Of_Birth, Register_date, Schedule_Constraint, Password):
        self.Family_name = Family_name
        self.Date_Of_Birth = Date_Of_Birth
        self.Register_date = Register_date
        self.Schedule_Constraint = Schedule_Constraint
        self.Password = Password

# Export form
class ExportTaskForm(FlaskForm):
    task_name = StringField('Task Name', validators=[InputRequired()])
    description = TextAreaField('Description')
    start_date = DateTimeLocalField('Start Date', format='%Y-%m-%dT%H:%M', validators=[InputRequired()])
    end_date = DateTimeLocalField('End Date', format='%Y-%m-%dT%H:%M', validators=[InputRequired()])