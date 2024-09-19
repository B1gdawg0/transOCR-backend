import os
from flask import Blueprint

user_group = Blueprint("user", __name__)



from . import routes