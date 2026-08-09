import os

from quart import Blueprint
from utils import load_modules

routes = Blueprint("routes", __name__)

load_modules(os.listdir(),__name__)