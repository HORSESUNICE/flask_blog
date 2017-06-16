from flask import Blueprint

fd = Blueprint('fd', __name__)

from . import views