import asyncio
import json
import time
from threading import Thread
from typing import Callable, List

from waterrower_websocket_server.interface import IRower, Event
from waterrower_websocket_server.server import WaterrowerWebsocketServer


def load_events(filename: str):
    with open(filename) as f:
        return [Event(e["type"], e["value"], e["raw"], e["timestamp"]) for e in json.load(f)]


class MockRower(IRower):
    def __init__(self, events: List[Event] = None):
        self._events = events or load_events("resources/events.json")

        self._counter = 0
        self._thread = Thread(target=self.run)
        self._stop = False
        self._callbacks = set()

    def register_callback(self, callback: Callable[[Event], None]) -> None:
        self._callbacks.add(callback)

    def run(self):
        time.sleep(5)
        while not self._stop:
            for callback in self._callbacks:
                if self._counter >= len(self._events):
                    self._counter = 0
                event = self._events[self._counter]
                event.timestamp = int(time.time()*1000)
                callback(event)
                self._counter += 1

            time.sleep(0.01)

    def start(self):
        self._thread.start()


def main():
    rower = MockRower()
    rower.start()

    server = WaterrowerWebsocketServer(rower, host="localhost", port=9899)
    asyncio.run(server.start())


if __name__ == "__main__":
    main()
