from .node import Node, NodeTemplate
from .graph import ComputeGraph

from . import components


def import_nodes():
    import os
    import sys
    import glob
    import logging
    import importlib.util
    import importlib.machinery

    from os import environ as env

    import api.utils as utils

    logger = logging.getLogger(__name__)

    for dir in os.listdir(node_path := os.path.join(env["DATA_DIR"], "nodes")):
        if (dir).startswith("__") and dir.endswith("__"):
            continue

        spec = importlib.machinery.ModuleSpec(
            module_name := f"api.compute.graph.nodes.{dir}", None, is_package=True
        )
        spec.submodule_search_locations.append(os.path.join(node_path, dir))

        module = importlib.util.module_from_spec(spec)

        sys.modules[module_name] = module

        for path in glob.glob(os.path.join(node_path, dir, "*.py")):
            subspec = importlib.util.spec_from_file_location(
                submodule_name := f"api.compute.graph.nodes.{dir}.{os.path.splitext(os.path.basename(path))[0]}",
                path,
            )
            logger.info(f"Importing file {path} to {submodule_name}")
            submodule = importlib.util.module_from_spec(subspec)
            sys.modules[submodule_name] = submodule
            subspec.loader.exec_module(submodule)
