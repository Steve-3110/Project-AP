# library setup
import requests # Used to check if the login page is already open on the default browser
import webbrowser # used to open the login page on the default browser on the run
import csv
from app_class import Task
from flask_mail import Message
from flask_mail import Mail
import os
import pandas as pd
import re
import unicodedata


# Function to check if the url is alrealy active in the default browser
def is_login_page_open(url):
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.ConnectionError:
        return False
    

# Function that open the browser on the desired URL
def open_login_page(url):
    webbrowser.open(url)

# Save the new tasks into a csv file dedicated
def save_tasks_to_csv(task):
    with open("tasks.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        # Check if the file is empty, if so, write the header row
        if file.tell() == 0:
            writer.writerow(["Name", "Priority", "Duration", "Dependency", "Time","Resources","User_name"])
        # Nettoyer les entrées utilisateur avant de les enregistrer
        cleaned_name = clean_input(task.name)
        if is_input_valid(cleaned_name):
            writer.writerow([cleaned_name, task.priority, task.duration, task.predecessor,task.time, task.resources, task.user_name])
        else:
            # Gérer les cas où l'entrée n'est pas valide
            print("Invalid input. Special characters or forbidden characters are not allowed.")


def read_tasks_from_csv(file_path):
    tasks = []
    with open(file_path, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Create a Task object from each row in the CSV file
            task = Task(
                name=row["Name"],
                duration=int(row["Duration"]),
                priority=row["Priority"],
                predecessor=row["Dependency"],  # Keep it as a string
                resources=row["Resources"],
                user_name=row["User_name"]
            )
            tasks.append(task)
    return tasks



def write_tasks_to_csv(tasks, csv_file_path="tasks.csv"):
    # Define the fieldnames for the CSV file
    fieldnames = ["Name", "Priority", "Duration", "Dependency", "Time","Resources","User_name"]

    # Write tasks to the CSV file
    with open(csv_file_path, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Write header
        writer.writeheader()

        # Write each task
        for task in tasks:
            writer.writerow({
                "Name": task.name,
                "Priority": task.priority,
                "Duration": task.duration,
                "Dependency": task.predecessor,
                "Time":task.time,
                "Resources": task.resources,
                "User_name": task.user_name
            })


def write_to_file(filename, message):
    with open(filename, 'a') as file:
        file.write(message + '\n')


def remove_task_from_csv(username, task_name, csv_file):
    # Créer un fichier temporaire pour écrire les tâches sans la tâche à supprimer
    temp_file = 'temp_tasks.csv'

    # Ouvrir les fichiers CSV
    with open(csv_file, mode='r') as file, open(temp_file, mode='w', newline='') as temp:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(temp, fieldnames=fieldnames)
        writer.writeheader()

        # Copier les tâches sauf celle à supprimer dans le fichier temporaire
        for row in reader:
            if row['User_name'] == username and row['Name'] != task_name:
                writer.writerow(row)

    # Renommer le fichier temporaire pour remplacer le fichier original
    os.remove(csv_file)
    os.rename(temp_file, csv_file)


def get_user_tasks(username, csv_file):
    user_tasks = []
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['User_name'] == username:
                # Create a task object
                task = Task(
                    name=row['Name'],
                    priority=int(row['Priority']),
                    duration=int(row['Duration']),
                    predecessor=str(row['Dependency']),
                    resources=row['Resources'],
                    user_name=str(row['User_name']),
                    time=row.get('Time', None)  # Utilisez la valeur de la colonne 'Time' si elle existe, sinon None
                )
                user_tasks.append(task)
    return user_tasks

def get_user_tasks_name(username,file):
    # Read the tasks from the CSV file
    tasks = []
    with open(file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['User_name'] == username:  # Vérifie si la tâche appartient à l'utilisateur
                tasks.append(row)
    return tasks

# Définir la fonction pour transformer une liste en une liste d'objets Task
def convert_to_task_objects(task_list):
    task_objects = []
    for task_data in task_list:
        # Créer un objet Task à partir des données de la tâche
        task = Task(
            name=task_data['Name'],
            priority=int(task_data['Priority']),
            duration=int(task_data['Duration']),
            predecessor=task_data['Dependency'],
            resources=task_data['Resources'],
            user_name=task_data['User_name']
        )
        task_objects.append(task)
    return task_objects




# Get a list of the user_name and password in the data base

def get_user_name_and_password(file):
    # Data initialization
    # Getting the list of register user_name
    df_user_name = pd.read_csv(file)
    username_list = df_user_name['user_name'].tolist()
    password_list = df_user_name['password'].tolist()

    return username_list, password_list



# Function to control the input of the users
def clean_input(input_string):
    # Supprimer les caractères spéciaux sauf les lettres, les chiffres et les espaces
    clean_string = re.sub(r'[^\w\s]', '', input_string)
    # Normaliser les caractères Unicode pour remplacer les lettres accentuées par leurs équivalents non accentués
    clean_string = unicodedata.normalize('NFKD', clean_string).encode('ASCII', 'ignore').decode('ASCII')
    return clean_string

def is_input_valid(input_string):
    # Vérifier si l'entrée contient des caractères interdits
    forbidden_chars = [',', '.', '?']
    for char in forbidden_chars:
        if char in input_string:
            return False
    return True

def contains_forbidden_chars(input_string):
    # Liste des caractères interdits
    forbidden_chars = [',', '.', '?',"!","à","é","è"]
    # Vérifier si l'entrée contient des caractères interdits
    for char in forbidden_chars:
        if char in input_string:
            return True
    return False