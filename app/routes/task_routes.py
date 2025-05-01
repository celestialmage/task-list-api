from flask import Blueprint, abort, make_response, request, Response
from app.models.task import Task
from sqlalchemy import func
from .route_utilities import validate_model
from ..db import db

bp = Blueprint("task_bp", __name__, url_prefix='/tasks')

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
    sort_by = request.args.get("sort_by")

    query = sort_tasks_by(sort_by)

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

def sort_tasks_by(sort_by):

    VALID_SORTS = ["title", "is_complete"]

    if sort_by and sort_by in VALID_SORTS:

        if sort_by == "title":
            query = db.select(Task).order_by(func.lower(Task.title))
        else:
            query = db.select(Task).order_by(Task.completed_at)

    elif sort_by:

        response = {
            "details": 
            f"Sort query {sort_by} was not recognized. Valid sort options are 'id', 'title', and 'is_complete'."
        }
        
        abort(make_response(response, 400))
    else:
        query = db.select(Task).order_by(Task.id)

    return query