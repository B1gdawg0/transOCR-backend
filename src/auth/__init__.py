import os
from flask import Blueprint


auth_group = Blueprint("auth", __name__)

from . import routes