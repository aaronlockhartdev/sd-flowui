class Node:
    def __init__(self, inputs: dict, outputs: dict, params: dict) -> None:
        self.inputs = inputs
        self.outputs = outputs
        self.params = params

        print(params)

        for k, v in self.params.items():
            if "default" in v:
                setattr(self, k, v["default"])

    def set_params(self, **kwargs: dict) -> None:
        for k, v in kwargs:
            assert k in self.params and v.isinstance(self.params[k]["type"])

            setattr(self, k, v)


class StartNode(Node):
    def __init__(self, outputs: dict, params: dict) -> None:
        super().__init__(None, outputs, params)


class EndNode(Node):
    def __init__(self, inputs: dict, params: dict) -> None:
        super().__init__(inputs, None, params)
