from flask import Blueprint, abort, make_response, request, Response
from ..models.goal import Goal
from .route_utilities import validate_model
from ..models.task import Task
from ..db import db

bp = Blueprint("goal_bp", __name__, url_prefix="/goals")


@bp.post("")
def create_goal():
    request_body = request.get_json()

    try:
        new_goal = Goal.from_dict(request_body)

    except KeyError as error:
        response = {"details": f"Invalid data"}
        abort(make_response(response, 400))

    db.session.add(new_goal)
    db.session.commit()

    return {"goal": new_goal.to_dict()}, 201


@bp.get("")
def get_all_goals():
    title_param = request.args.get("title")
    sort = request.args.get("sort")

    query = db.select(Goal)

    if title_param:
        query = query.where(goal.title.ilike(f"%{title_param}%"))

    goals = db.session.scalars(query)

    goals_response = []

    for goal in goals:
        goals_response.append(goal.to_dict())

    return goals_response


@bp.get("/<goal_id>")
def get_single_goal(goal_id):

    goal = validate_model(Goal, goal_id)

    return {
        "goal": goal.to_dict()
    }


@bp.get("/<goal_id>/tasks")
def get_tasks_for_goal(goal_id):

    goal = validate_model(Goal, goal_id)

    query = db.select(Task).where(Task.goal_id == goal_id)

    goal_dict = goal.to_dict()

    tasks = db.session.scalars(query)

    goal_dict["tasks"] = [task.to_dict() for task in tasks]

    return goal_dict


@bp.delete("/<goal_id>")
def remove_goal(goal_id):

    goal = validate_model(Goal, goal_id)

    db.session.delete(goal)
    db.session.commit()

    return Response(status=204, mimetype='application/json')


@bp.put("/<goal_id>")
def update_goal(goal_id):

    goal = validate_model(Goal, goal_id)

    request_body = request.get_json()

    try:
        goal.title = request_body["title"]
    except KeyError as error:
        response = {"details": f"Request missing '{error.args[0]}' attribute"}
        abort(make_response(response, 400))

    db.session.commit()

    return {"goal": goal.to_dict()}, 204


@bp.post("/<goal_id>/tasks")
def update_goal_with_tasks(goal_id):

    goal = validate_model(Goal, goal_id)

    request_body = request.get_json()

    task_ids = request_body["task_ids"]

    goal.tasks = []

    for id in task_ids:

        task = validate_model(Task, id)

        task.goal_id = goal.id

        goal.tasks.append(task)

    db.session.commit()

    return {
        "id": goal.id,
        "task_ids": task_ids
    }, 200
