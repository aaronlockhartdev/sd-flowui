from .node import Node, NodeTemplate
from .graph import ComputeGraph

from . import components


import os
import sys
import glob
import logging
import logging.config
import importlib.util
import importlib.machinery

from os import environ as env

import api.utils as utils

logging.config.dictConfig(utils.LOGGING_CONFIG)
logger = logging.getLogger(__name__)

nodes_path = os.path.join(env["DATA_DIR"], "nodes")

nodes_spec = importlib.machinery.ModuleSpec(
    nodes_name := f"api.compute.graph.nodes", None, is_package=True
)
nodes_spec.submodule_search_locations.append(nodes_path)

nodes = importlib.util.module_from_spec(nodes_spec)
sys.modules[nodes_name] = nodes


def load_module(package_name: str, module_path):
    module_spec = importlib.util.spec_from_file_location(
        module_name := f"{package_name}.{os.path.splitext(os.path.basename(module_path))[0]}",
        module_path,
    )
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_name] = module
    module_spec.loader.exec_module(module)

    return module_name


def load_package(package_path):
    package_spec = importlib.machinery.ModuleSpec(
        package_name := f"{nodes_name}.{os.path.splitext(os.path.basename(package_path))[0]}",
        None,
        is_package=True,
    )
    package_spec.submodule_search_locations.append(package_path)

    package = importlib.util.module_from_spec(package_spec)

    sys.modules[package_name] = package

    return package_name


for module_path in glob.glob(os.path.join(nodes_path, "*.py")):
    module_name = load_module(nodes_name, module_path)
    logger.info(f"Loaded nodes submodule {module_name}")

for package_path in glob.glob(os.path.join(nodes_path, "*")):
    if not os.path.isdir(package_path) or os.path.basename(package_path).startswith(
        "__"
    ):
        continue

    package_name = load_package(package_path)
    logger.info(f"Loaded nodes subpackage {package_name}")

    for module_path in glob.glob(os.path.join(package_path, "*.py")):
        module_name = load_module(package_name, module_path)
        logger.info(f"Loaded {package_name.split('.')[-1]} submodule {module_name}")
