import os
import signal
import asyncio
import networkx as nx
import multiprocessing as mp
from multiprocessing.connection import Connection
from typing import Any

import api.services as services

from . import graph


class Executor:
    def __init__(self, queue: mp.Queue = None):
        self.queue = queue if queue else mp.Queue()
        self._pipe, child_pipe = mp.Pipe()
        self._process = mp.Process(
            target=process, args=(self.queue, child_pipe), daemon=True
        )
        self._pipe_callback = asyncio.Event()

        asyncio.get_event_loop().add_reader(
            self._pipe.fileno(), self._pipe_callback.set
        )

    async def __call__(self):
        self._process.start()
        while True:
            await self._pipe_callback.wait()

            data = self._pipe.recv()

            print(data)

            # TODO: do something with data

            self._pipe_callback.clear()

    def enqueue(self, graph: graph.ComputeGraph, id: int | None = None):
        self.queue.put_nowait((id, graph))

    def pause(self):
        os.kill(self._process.pid, signal.SIGSTOP)

    def resume(self):
        os.kill(self._process.pid, signal.SIGCONT)

    def interrupt(self):
        os.kill(self._process.pid, signal.SIGINT)


def process(queue: mp.Queue, pipe: Connection):
    cache: dict[str, Any] = {}
    while True:
        try:
            id: int
            graph_: graph.ComputeGraph

            id, graph_ = queue.get()

            if not nx.is_directed_acyclic_graph(graph_):
                raise Exception("Graph contains cycle")

            components = nx.weakly_connected_components(graph_)

            component: dict[int, graph.Node] = {
                n: graph_.nodes[n]["obj"]
                for n in (
                    next(c for c in components if id in c)
                    if id
                    else max(components, key=len)
                )
            }

            input_nodes = {k: v for k, v in component.items() if not v.template.inputs}

            pipe.send({"type": "info", "data": input_nodes})

        except KeyboardInterrupt:
            continue
        except Exception as e:
            pipe.send({"type": "error", "data": e})


executor = Executor()
