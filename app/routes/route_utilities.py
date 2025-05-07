from flask import abort, make_response
from ..db import db

def validate_model(cls, model_id):

    try:
        model_id = int(model_id)
    except:
        response = {"message": f"{cls.__name__} {model_id} invalid."}
        abort(make_response(response, 400))

    query = db.select(cls).where(cls.id == model_id)
    model = db.session.scalar(query)

    if not model:
        response = {"message": f"{cls.__name__} {model_id} not found."}
        abort(make_response(response, 404))

    return model

def model_from_request(cls, request):

    request_body = request.get_json()

    try:
        model_dict = cls.from_dict(request_body)
    except KeyError as error:
        response = {"details": "Invalid data"}
        abort(make_response(response, 400))

    return model_dict