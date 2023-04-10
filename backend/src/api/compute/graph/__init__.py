import os
import sys
import glob
import importlib.util

from os import environ as env

for path in glob.glob(os.path.join(env["DATA_DIR"], "nodes", "*.py")):
    spec = importlib.util.spec_from_file_location(
        module_name := f"nodes.{os.path.splitext(os.path.basename(path))[0]}", path
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
