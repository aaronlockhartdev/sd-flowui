class Node:
    def __init__(self, state: dict):
        self.state = state
        self.params = {k: v["value"] for k, v in self.state["parameters"].items()}

    @property
    def params(self) -> dict:
        return {k: getattr(self, f"_{k}") for k in self.state["parameters"]}

    @params.setter
    def params(self, params: dict):
        for k, v in params.items():
            setattr(self, f"_{k}", v)
            self.state["parameters"][k]["value"] = v
