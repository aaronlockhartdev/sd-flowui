import os
import torch
import torch._dynamo
import signal
import asyncio
import traceback
import networkx as nx
import multiprocessing as mp
from multiprocessing.connection import Connection
from multiprocessing.synchronize import Event

import logging
import logging.config

from typing import Any
from enum import Enum
from pydantic import BaseModel

import api.utils as utils
import api.services as services

from . import graph

logging.config.dictConfig(utils.LOGGING_CONFIG)
logger = logging.getLogger(__name__)


class Executor:
    def __init__(self, device: torch.device, queue: mp.Queue = None):
        self._device = device
        self._queue = queue if queue else mp.Queue()
        self._pipe, child_pipe = mp.Pipe()
        self._shutdown_event = mp.Event()
        self._process = mp.Process(
            target=process, args=(device, self._queue, child_pipe, self._shutdown_event)
        )
        self._pipe_callback = asyncio.Event()

        asyncio.get_event_loop().add_reader(
            self._pipe.fileno(), self._pipe_callback.set
        )

    async def __call__(self):
        self._process.start()
        while not self._pipe.closed:
            await self._pipe_callback.wait()

            data = self._pipe.recv()

            d = {"device": f"{self._device.type}:{self._device.index}"}

            match data.type:
                case IPCMessageType.ERROR:
                    logger.error(data.msg, extra=d)
                case IPCMessageType.INFO:
                    logger.info(data.msg, extra=d)

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

    def cleanup(self):
        self._queue.close()

        asyncio.get_event_loop().remove_reader(self._pipe.fileno())

        self._pipe.close()

        self._shutdown_event.set()
        self.interrupt()
        self._process.join()


class IPCMessageType(Enum):
    ERROR = "error"
    INFO = "info"


class IPCMessage(BaseModel):
    type: IPCMessageType
    msg: str


def process(device, queue: mp.Queue, pipe: Connection, shutdown_event: Event):
    import warnings

    warnings.filterwarnings("error")

    torch.set_default_device(device)

    cache: dict[str, Any] = {}
    while not shutdown_event.is_set():
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

                    try:
                        outputs[k] = v(**inputs)

                    except Exception:
                        pipe.send(
                            IPCMessage(
                                type=IPCMessageType.ERROR,
                                msg=f"Node '{k}' ({type(v).__name__}) raised an exception \n{traceback.format_exc()}",
                            )
                        )
                        return

            pipe.send(IPCMessage(type=IPCMessageType.INFO, msg="Compiled torch graph"))
            exec()

        except KeyboardInterrupt:
            continue
        except RuntimeWarning:
            pipe.send(
                IPCMessage(
                    type=IPCMessage.WARNING,
                    msg=warnings.formatwarning(),
                )
            )
            continue
        except Exception:
            pipe.send(
                IPCMessage(
                    type=IPCMessageType.ERROR,
                    msg=traceback.format_exc(),
                )
            )
            continue

    pipe.close()


executor = Executor(torch.device("cpu", 0))
