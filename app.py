# library setup
from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired
from datetime import datetime as dt
import pandas as pd
from wtforms.validators import InputRequired, EqualTo
import threading
from app_class import *
from function_app import open_login_page, save_tasks_to_csv, read_tasks_from_csv,write_tasks_to_csv,remove_task_from_csv,get_user_tasks,convert_to_task_objects
from function_app import get_user_name_and_password,clean_input,contains_forbidden_chars,get_user_tasks_name
import csv
import os 
from email.message import EmailMessage
import smtplib 
import ssl
from icalendar import Calendar, Event
import bcrypt

########################################################################
################################ Set up ################################
########################################################################
# Set up of Flask
app = Flask(__name__) # define the app.py file as the root path of the application
app.config['SECRET_KEY'] = 'secret' # cyber security stuff, should use random generate numbers to protect the app

# Variable set up
# File names
user_name_file = "user_name.csv"
task_file = "tasks.csv"

###########################################################################
################################ Functions ################################
###########################################################################
# Custom validator to check if the duration is positive - To be adjusted as the login error
def positive_duration(form, field):
    if field.data <= 0:
        flash('Duration must be a positive integer', 'error')
        raise ValidationError('Duration must be a positive integer')

#######################################################################
################################ Route ################################
#######################################################################

################################ LOGIN ################################
@app.route('/')
def login():
    return render_template('login.html') # Display the home page

# Route for the login validation
@app.route('/login', methods=['POST'])
def login_post():
    # Get the list of the password and the user name in the data base
    user_name, passwords = get_user_name_and_password(user_name_file)
    # Get the value in the form of the username and the password
    username = str(request.form['username'])
    password = str(request.form['password'])
    # Check if the username exists in the user_name list
    if str(username) in user_name:
        # Get the index of the username in the user_name list
        user_index = user_name.index(username)
        # Check if the password matches the hashed password at the same index in the passwords list
        hashed_password = passwords[user_index]
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            # If the login is validate we can go find the tasks of the current user
            df_tasks = pd.read_csv(task_file)
            # keep only the tasks for the concerned user
            df_tasks = df_tasks[df_tasks['User_name'] == username]
            # If the password matches, allow the user to access the dashboard
            # Pass the username as an argument to the dashboard
            # Get the tasks of the current logged-in user
            tasks = get_user_tasks(username,task_file)
            # Display the dashboard with the task of the logged-in user
            return render_template('dashboard.html', username=username,tasks=tasks)
        else :
            error = "Invalid password. Please try again or register "
    else :
        error = "Invalid username. Please try again or register "
    # If the username or password is incorrect, display an error message
    return render_template('login.html', error=error)


################################ DASHBOARD ################################
# Route for dashboard, pass the username argument to display it
@app.route('/dashboard/<username>')
def dashboard(username):
    # Get the current users task to display them properly on the dashboard
    tasks = get_user_tasks(username,task_file)
    return render_template('dashboard.html', username=username,tasks=tasks)

################################ ADD_TASK ################################
@app.route('/add_task', methods=['POST'])
def add_task():
    username = request.form['username']  # Get the username from the form data
    df_tasks = pd.read_csv(task_file)
   # keep only the tasks for the concerned user
    df_tasks = df_tasks[df_tasks['User_name'] == username]
    # If the password matches, allow the user to access the dashboard
    # Pass the username as an argument to the dashboard
    # Extract dependency choices from tasks
    dependency_choices = [("", "None")]  # Add an empty option
    dependency_choices += [(dep, dep) for dep in df_tasks['Name'].unique()]
    form = TaskForm(dependency_choices=dependency_choices)
    form.predecessor.choices = dependency_choices

    if form.validate_on_submit():
        # Check if the task name already exists
        task_name = clean_input(form.name.data)
        existing_tasks = [task.name for task in get_user_tasks(username, task_file)]
        if task_name in existing_tasks:
            flash('Task name already exists. Please choose a different name.', 'error')
        else:
            # Process the form data and add the task
            task = Task(
                name=form.name.data,
                priority=form.priority.data,
                duration=form.duration.data,
                predecessor=form.predecessor.data,
                resources=form.resources.data,
                user_name=username
            )
            # Adding the tasks to the csv tasks
            save_tasks_to_csv(task)
            # Get the tasks of the current user, to display it on the dashboard page
            tasks = get_user_tasks(username, task_file)
            # Redirect back to the dashboard page after adding the task
            return render_template('dashboard.html', username=username, tasks=tasks)
    return render_template('index.html', form=form, username=username)

################################ delete_TASK ################################
# Routing when user press to delete a task
@app.route('/delete_task/<task_name>', methods=['POST'])
def remove_task(task_name):
    # Get the user name
    username = request.form.get('username')
    # Get all the user's tasks name
    current_tasks = get_user_tasks(username,task_file)
    # Load tasks for the user
    df_tasks = pd.read_csv(task_file)
    df_user_tasks = df_tasks[df_tasks['User_name'] == username]
    # Extract dependency choices from tasks
    dependency_choices = df_user_tasks['Dependency'].unique().tolist()
    # add a condition that don't allow the removing if the task is a predecessor for another one
    if task_name not in dependency_choices:
        # Check if the task is a predecessor for any other task
        if not df_tasks[df_tasks['Dependency'] == task_name].empty:
            flash('This task is related to other tasks. You cannot remove this one without removing the others first.', 'error')
            remaining_tasks = get_user_tasks(username, task_file)
            return render_template('dashboard.html', username=username, tasks=remaining_tasks)

        # Supprimer la tâche du fichier CSV
        remove_task_from_csv(username, task_name, task_file)

        # Récupérer les tâches restantes de l'utilisateur
        remaining_tasks = get_user_tasks(username, task_file)
        # Rediriger vers le tableau de bord avec les tâches mises à jour
        return render_template('dashboard.html', username=username, tasks=remaining_tasks)
    else:
        flash('This task is related to other tasks, you cannot remove this one, without removing the others', 'error')
        return render_template('dashboard.html', username=username, tasks=current_tasks)


################################ REGISTER ################################
# Set the Route for registering process
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Create the form using the registration form class
    form = RegistrationForm()
    # If the entry is valid --> go, else display error and stay on register page
    if form.validate_on_submit():
        # Get the value of the user's inputs
        user_name = form.user_name.data
        email = form.email.data
        family_name = form.family_name.data
        surname = form.surname.data
        dob = form.dob.data.strftime('%d.%m.%Y')
        password = form.password.data
        
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Get the users data
        df_user = pd.read_csv(user_name_file)
        # Check that the username doesn't already exists in the data base (.csv)
        if user_name not in df_user["user_name"].values and email not in df_user["email"].values:
            # Check if inputs contain forbidden characters
            if not contains_forbidden_chars(user_name) \
                and not contains_forbidden_chars(family_name) and not contains_forbidden_chars(surname) \
                and not contains_forbidden_chars(password):
                # Store the new user in the .csv file of the users
                # Define the field types for each column
                field_types = [str, str, str, str, str, str]
                # Write the user data to the CSV file
                with open('user_name.csv', mode='a', newline='') as file:
                    writer = csv.writer(file)
                    # Convert each value to its appropriate type before writing
                    typed_data = [field_type(value) for field_type, value in zip(field_types, [user_name, family_name, surname, dob, hashed_password, email])]
                    writer.writerow(typed_data)
                # Sent an email to the new registered user
                sendemail(email)
                # Redirect to login page after successful registration
                return redirect(url_for('login'))
            else:
                flash('Invalid input. Special characters or forbidden characters are not allowed.', 'error')
        elif user_name in df_user["user_name"].values:
            flash('Username already exists. Please choose a different username.', 'error')

        elif email in df_user["email"].values:
            flash('e-mail already registered. Sign in via the login page', 'error')

    return render_template('register.html', form=form)

################################ LOGOUT ################################
@app.route('/logout', methods= ['POST'])
def logout():
    # Redirect the user back to the login page
    return redirect(url_for('login')) 

################################ LOGOUT ################################
@app.route('/info/<username>', methods=['GET'])
def info(username):
    # Redirect the user back to the login page
    return render_template('info.html', username=username)

#######################################################################
################################ ALGO ################################
#######################################################################
# Route for optimizing the schedule
@app.route('/optimize_schedule/<username>', methods=['POST'])
def optimize_schedule(username):
    
    
    # Get the task priority as integer
    def get_priority(task):
        return int(task.priority)
    
    # Priority Scheduling Algorithm
    def schedule_tasks():
        """
        This function implements the Priority and dependency Scheduling Algorithm to optimize task scheduling.
        """
        # Get the task of the user into a list
        tasks = get_user_tasks(username,task_file)
        
        # Sort tasks by priority
        sorted_tasks = sorted(tasks, key=get_priority, reverse=False)

        # Initialize the schedule and set of scheduled task names
        schedule = []
        scheduled_task_names = []

        # Maximum number of iterations without scheduling any task, avoid running forever
        max_iterations_without_scheduling = 10000
        iterations_without_scheduling = 0

        # Set up the unscheduled tasks (copy every tasks)
        unscheduled_tasks = sorted_tasks.copy()

        # Iterate until all tasks are scheduled and we reach the maximum iteration allowed
        while unscheduled_tasks and iterations_without_scheduling < max_iterations_without_scheduling:
            # Keep track of whether any tasks were scheduled in this iteration
            any_scheduled = False
            
            # Sort unscheduled tasks by priority
            unscheduled_tasks.sort(key=get_priority, reverse=False)

            for task in unscheduled_tasks:
                predecessor = task.predecessor
                if not predecessor:
                    new_task = Task(
                        name=task.name,
                        priority=task.priority,
                        duration=task.duration,
                        predecessor=task.predecessor,
                        resources=task.resources,
                        user_name=task.user_name,
                        time=task.time 
                    )
                    schedule.append(new_task)
                    scheduled_task_names.append(str(task.name))
                    unscheduled_tasks.remove(task)
                    any_scheduled = True
                    break
                else:
                    # Check if any predecessor is already scheduled
                    if str(predecessor) in scheduled_task_names:
                        new_task = Task(
                            name=task.name,
                            priority=task.priority,
                            duration=task.duration,
                            predecessor=task.predecessor,
                            resources=task.resources,
                            user_name=task.user_name,
                            time=task.time
                        )
                        schedule.append(new_task)
                        scheduled_task_names.append(str(task.name))
                        unscheduled_tasks.remove(task)
                        any_scheduled = True
                        break

            # If any task was scheduled in this iteration, reset the counter
            if any_scheduled:
                iterations_without_scheduling = 0
            else:
                iterations_without_scheduling += 1

        return schedule

    # Run the algorithm to schedule the tasks
    scheduled_tasks = schedule_tasks()
    optimization_time = dt.now()
    # Formatez la date et l'heure selon vos spécifications
    formatted_date_time = optimization_time.strftime("%H:%M %d-%m-%Y")
    
    # Redirect back to the dashboard page after optimization
    return render_template('dashboard.html', username=username,tasks=scheduled_tasks,optimization_time=formatted_date_time)


#######################################################################
################################ MAILING ################################
#######################################################################
# Setup the mailing system
email_sender = "ScheduleOptimizerap@gmail.com"
email_password = "yyhz oouv wrlr hjlp"
subject = "Thanks for registering on Schedule Optimizer"
body = """

Hi thanks for your registration, enjoy your new journey into schedule optimization !

Best regard,

The Schedule Optimizer team

"""
# Function to sent an e-mail after registering
def sendemail(email_reciever):

    em = EmailMessage()

    em["From"] = email_sender
    em["To"] = email_reciever
    em["subject"] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com",465,context=context) as smtp:
        smtp.login(email_sender,email_password)
        smtp.sendmail(email_sender,email_reciever,em.as_string())


#######################################################################
################################ CLASS ################################
#######################################################################
# Create the TaskForm class
class TaskForm(FlaskForm):
    name = StringField('Task Name:', validators=[DataRequired()], default='Exercises Advanced Programming')
    priority = SelectField('Priority:', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], validators=[DataRequired()])
    duration = IntegerField('Duration:', validators=[DataRequired(), positive_duration])
    predecessor = SelectField('Dependency:', choices=[])
    resources = StringField('Resources:')
    submit = SubmitField('Add Task')




##################################################################

###################### .ics part
# Routing for the tasks removing, click from dashboard
@app.route('/ics_export_form/<username>', methods=['GET'])
def ics_export_form(username):
    tasks_name = get_user_tasks_name(username, task_file)
    
    return render_template('ics_export.html', username=username, tasks=tasks_name)

# Routing when user press to export a task
@app.route('/export_task/<username>', methods=['POST'])
def export_task(username):
    
    tasks_name = get_user_tasks_name(username,task_file)
    form = ExportTaskForm(request.form)  # Create an instance of the form

    # Get the information of the selected task
    task_name = form.task_name.data

    # Convertir les dates de chaîne en objets datetime
    start_date = form.start_date.data
    end_date = form.end_date.data

    # Créez un événement dans le calendrier
    cal = Calendar()
    event = Event()
    event.add('summary', task_name)
    event.add('description', form.description.data)
    event.add('dtstart', start_date)
    event.add('dtend', end_date)
    cal.add_component(event)

    # Convertir le calendrier en format .ics
    ics_content = cal.to_ical()

    # Définir le nom de fichier pour le fichier .ics
    filename = f"{task_name}.ics"

    # Return a Flask response with the .ics content for downloading
    response = Response(
        ics_content,
        mimetype="text/calendar",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

    return response

#############################################################################
################################ APP RUNNING ################################
#############################################################################
if __name__ == '__main__':
    # Set the URL of the web app
    login_page_url = 'http://127.0.0.1:5000'
    # Start a new thread to open the login page on the default browser
    threading.Thread(target=open_login_page, args=(login_page_url,)).start()
    # Run the Flask app in the main thread
    app.run(debug=True, host='0.0.0.0', port=5000)
