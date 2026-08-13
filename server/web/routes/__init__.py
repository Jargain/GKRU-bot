import os
from pathlib import Path

from quart import Blueprint
from utils import load_modules

routes = Blueprint("routes", __name__)

current_dir = Path(__file__).parent

modules = [mod for mod in os.listdir(current_dir) if mod.endswith('.py') and mod != '__init__.py']

load_modules(module_list=modules,pkg_name='server.web.routes')