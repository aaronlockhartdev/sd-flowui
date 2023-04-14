import os
import torch
import signal
import asyncio
import traceback
import networkx as nx
import multiprocessing as mp
from multiprocessing.connection import Connection
from typing import Any

import api.services as services

from . import graph


class Executor:
    def __init__(self, device: torch.device, queue: mp.Queue = None):
        self._queue = queue if queue else mp.Queue()
        self._pipe, child_pipe = mp.Pipe()
        self._process = mp.Process(
            target=process, args=(self._queue, child_pipe), daemon=True
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
        self._queue.put_nowait((id, graph))

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

            exec_order: dict[int, graph.Node] = {
                n: graph_.nodes[n]["obj"]
                for n in nx.topological_sort(graph_)
                if n
                in set(
                    next(c for c in cs if id in c)
                    if id
                    else max(cs := nx.weakly_connected_components(graph_), key=len)
                )
            }

            @torch.compile
            def exec():
                outputs = {}
                for k, v in exec_order.items():
                    inputs = {
                        m[1]: outputs[n, m[0]]
                        for n in graph_.predecessors(k)
                        for m in graph_.edges[n, k]["map"]
                    }

                    outputs[k] = v(**inputs)

            exec()

        except KeyboardInterrupt:
            continue
        except Exception:
            pipe.send(
                {
                    "type": "error",
                    "data": traceback.format_exc(),
                }
            )
            continue


executor = Executor(torch.device("cuda", 0))
