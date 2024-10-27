import pytest
import websockets
from typing import Callable

from waterrower_websocket_server.interface import IRower, Event
from waterrower_websocket_server.server import WaterrowerWebsocketServer
import asyncio


class MockRower(IRower):
    def __init__(self):
        self.callbacks = []

    def send_event(self, event: Event):
        for callback in self.callbacks:
            callback(event)

    def register_callback(self, callback: Callable[[Event], None]) -> None:
        self.callbacks.append(callback)


class MockClient:
    def __init__(self, uri: str):
        self._uri = uri
        self.messages = []

    async def start(self):
        async with websockets.connect(self._uri) as websocket:
            while True:
                try:
                    message = await websocket.recv()
                    self.messages.append(message)

                except websockets.exceptions.ConnectionClosed:
                    break


@pytest.mark.asyncio
async def test_server_async():
    rower = MockRower()

    server = WaterrowerWebsocketServer(rower, host="localhost", port=9899)

    task = asyncio.create_task(server.start())
    await asyncio.sleep(0.2)

    client = MockClient("ws://localhost:9899")
    client_task = asyncio.create_task(client.start())
    await asyncio.sleep(0.2)

    rower.send_event(Event("my_event", 10, "RAWVALUE", 10))
    await asyncio.sleep(0.2)

    await server.stop()
    await task
    await client_task

    assert len(client.messages) == 1
