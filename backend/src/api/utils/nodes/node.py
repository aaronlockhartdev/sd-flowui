import copy


class Node:
    def __init__(self, inputs: dict = {}, params: dict = {}, outputs: dict = {}):
        self.template = {"inputs": inputs, "params": params, "outputs": outputs}
        self.params = {k: v["default"] for k, v in self.template["params"].items()}

    @property
    def params(self) -> dict:
        return {k: getattr(self, f"_{k}") for k in self.template["params"]}

    @params.setter
    def params(self, params: dict):
        for k, v in params.items():
            setattr(self, f"_{k}", v)

    @property
    def state(self) -> dict:
        state = copy.deepcopy(self.template)

        for k, v in state["params"].items():
            del v["default"]
            v["value"] = getattr(self, f"_{k}")
            v["type"] = v["type"].__qualname__

        for k, v in state["inputs"].items():
            v["type"] = v["type"].__qualname__

        for k, v in state["outputs"].items():
            v["type"] = v["type"].__qualname__

        return state
