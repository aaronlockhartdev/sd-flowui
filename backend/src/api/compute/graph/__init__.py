from .node import Node, NodeTemplate
from .graph import ComputeGraph

from . import components


def import_nodes():
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

    parent_spec = importlib.machinery.ModuleSpec(
        nodes_package := f"api.compute.graph.nodes", None, is_package=True
    )
    parent_spec.submodule_search_locations.append(nodes_path)

    def import_package(dir: str) -> tuple:
        spec = importlib.machinery.ModuleSpec(
            package_name := f"api.compute.graph.nodes.{dir}", None, is_package=True
        )

        spec.submodule_search_locations.append(os.path.join(nodes_path, dir))

        package = importlib.util.module_from_spec(spec)

        return package_name, package

    def import_module(package_name: str, path: str) -> tuple:
        spec = importlib.util.spec_from_file_location(
            module_name := f"{package_name}.{os.path.splitext(os.path.basename(path))[0]}",
            path,
        )

        module = importlib.util.module_from_spec(spec)

        return module_name, module

    for path in glob.glob(os.path.join(nodes_path, "*.py")):
        module_name, module = import_module(nodes_package, path)
        logger.info(f"Importing module {module_name}")
        sys.modules[module_name] = module

    for dir in os.listdir(nodes_path):
        if not os.path.isdir(os.path.join(nodes_path, dir)) or (
            dir.startswith("__") and (dir.endswith("__"))
        ):
            continue

        package_name, package = import_package(dir)
        logger.info(f"Importing package {package_name}")
        sys.modules[package_name] = package

        for path in glob.glob(os.path.join(nodes_path, dir, "*.py")):
            module_name, module = import_module(package_name, path)
            logger.info(f"Importing submodule {module_name}")
            sys.modules[module_name] = module
