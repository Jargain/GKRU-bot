import mimetypes
from importlib import import_module
from pathlib import Path
from typing import Callable


def load_modules(module_list,pkg_name):
    for module in module_list:

        if "python" not in str(mimetypes.guess_type(module)[0]):
            continue

        mod = Path(module).stem
        if mod == "__init__":
            continue

        import_module(pkg_name + "." + mod, pkg_name)