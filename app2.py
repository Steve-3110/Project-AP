from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Change this to a random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'  # Database file will be created in the project folder
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# app.py (continue)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)




# app.py (continue)
from flask import redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Implement user registration logic here
    pass

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Implement user login logic here
    pass

@app.route('/dashboard')
@login_required
def dashboard():
    # Implement displaying user tasks on the dashboard
    pass

@app.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
    # Implement adding a new task logic here
    pass

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    # Implement editing an existing task logic here
    pass

@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    # Implement deleting a task logic here
    pass





