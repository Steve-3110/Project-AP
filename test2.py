import pandas as pd
from function_app import get_user_tasks
import datetime as dt
from app_class import Task

# Get the task of the user into a list
tasks = get_user_tasks("Luca Marini","tasks.csv")

#for task in tasks:
 #   print(task.name)

# Get the task priority as integer
def get_priority(task):
    return int(task.priority)

# Priority Scheduling Algorithm
# Priority Scheduling Algorithm
def schedule_tasks():
    # Get the task of the user into a list
    tasks = get_user_tasks("Luca Marini","tasks.csv")
    for task in tasks:
        print(task.name)
    

    # Sort tasks by priority
    sorted_tasks = sorted(tasks, key=get_priority, reverse=False)
    # Get the time of the optimization
    #LastRunAlgo = dt.now()

    # Initialize the schedule and set of scheduled task names
    schedule = []
    scheduled_task_names = []

    # Maximum number of iterations without scheduling any task
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
            #print(predecessor)
            if not predecessor:
                new_task = Task(
                    name=task.name,
                    priority=task.priority,
                    duration=task.duration,
                    predecessor=task.predecessor,
                    resources=task.resources,
                    user_name=task.user_name
                )
                schedule.append(new_task)
                scheduled_task_names.append(str(task.name))
                unscheduled_tasks.remove(task)
                any_scheduled = True
                #print(scheduled_task_names)
                #print(predecessor)
                #print("Test" in scheduled_task_names)
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
                        user_name=task.user_name
                    )
                    schedule.append(new_task)
                    scheduled_task_names.append(str(task.name))
                    unscheduled_tasks.remove(task)
                    any_scheduled = True
                    print(scheduled_task_names)
                    break

        # If any task was scheduled in this iteration, reset the counter
        if any_scheduled:
            iterations_without_scheduling = 0
        else:
            iterations_without_scheduling += 1


    return schedule

# Run the algorithm to schedule the tasks
scheduled_tasks = schedule_tasks()


