from flask import Blueprint

bp = Blueprint('main', __name__)

@bp.route('/')
def show():
    return "Test test"