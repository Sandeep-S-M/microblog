from flask import Blueprint

bp = Blueprint('errors', __name__)

from microblog.error_handlers import handlers
