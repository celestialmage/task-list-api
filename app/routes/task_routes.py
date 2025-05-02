from flask import Blueprint, abort, make_response, request, Response
from datetime import date
from app.models.task import Task
from sqlalchemy import func, desc
from .route_utilities import validate_model
from ..db import db
import os
import requests

bp = Blueprint("task_bp", __name__, url_prefix='/tasks')

SLACK_URL = 'https://slack.com/api/chat.postMessage'

@bp.post("")
def create_task():
    request_body = request.get_json()

    try:
        new_task = Task.from_dict(request_body)

    except KeyError as error:
        response = {"details": f"Invalid data"}
        abort(make_response(response, 400))

    db.session.add(new_task)
    db.session.commit()

    return {"task": new_task.to_dict()}, 201

@bp.get("")
def get_all_tasks():

    title_param = request.args.get("title")
    description_param = request.args.get("description")
    sort = request.args.get("sort")

    query = sort_tasks_by(sort)

    if title_param:
        query = query.where(Task.title.ilike(f"%{title_param}%"))

    if description_param:
        query = query.where(Task.description.ilike(f"%{description_param}%"))

    tasks = db.session.scalars(query)

    tasks_response = []

    for task in tasks:
        tasks_response.append(task.to_dict())

    return tasks_response

@bp.get("/<task_id>")
def get_single_task(task_id):

    task = validate_model(Task, task_id)

    return {
        "task": task.to_dict()
    }

@bp.patch("/<task_id>/mark_complete")
def mark_task_complete(task_id):

    task = validate_model(Task, task_id)

    task = change_status(task, True)

    db.session.commit()

    api_key = os.environ.get('SLACK_API_KEY')

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    slack_message = {
        "channel": "test-slack-api",
        "text": f"Someone just completed the task {task.title}",
    }

    result = requests.post(url=SLACK_URL, json=slack_message, headers=headers)

    return result._content

@bp.patch("/<task_id>/mark_incomplete")
def mark_task_incomplete(task_id):

    task = validate_model(Task, task_id)

    task = change_status(task, False)

    db.session.commit()

    return Response(status=204, mimetype='application/json')

@bp.delete("/<task_id>")
def remove_task(task_id):

    task = validate_model(Task, task_id)

    db.session.delete(task)
    db.session.commit()

    return Response(status=204, mimetype='application/json')

@bp.put("/<task_id>")
def update_task(task_id):

    task = validate_model(Task, task_id)

    request_body = request.get_json()

    try:
        task.title = request_body["title"]
        task.description = request_body["description"]
        task.completed_at = request_body.get("complete_at")
    except KeyError as error:
        response = {"details": f"Request missing '{error.args[0]}' attribute"}
        abort(make_response(response, 400))

    db.session.commit()

    return {"task": task.to_dict()}, 204

def change_status(task, is_complete):

    if is_complete and not task.completed_at:
        task.completed_at = date.today()
    elif not is_complete and task.completed_at:
        task.completed_at = None

    return task


def sort_tasks_by(sort):

    VALID_SORTS = ["asc", "desc"]

    if sort and sort in VALID_SORTS:

        if sort == "asc":
            query = db.select(Task).order_by(Task.title)
        else:
            query = db.select(Task).order_by(desc(Task.title))

    elif sort:

        response = {
            "details": 
            f"Sort query {sort} was not recognized. Valid sort options are {", ".join(VALID_SORTS)}."
        }
        
        abort(make_response(response, 400))
    else:
        query = db.select(Task).order_by(Task.completed_at)

    return query