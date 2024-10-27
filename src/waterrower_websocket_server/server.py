import logging
import json

import asyncio
import signal

import websockets

from waterrower_websocket_server.interface import Event, IRower


logger = logging.getLogger(__name__)


class WaterrowerWebsocketServer:
    def __init__(self, rower: IRower, host: str, port: int):
        self._rower = rower
        self._host = host
        self._port = port
        self._clients = set()

        self._stop = None

        rower.register_callback(self.handle_event)

    async def send_event(self, client, event):
        await client.send(json.dumps(self.serialize_event(event)))

    def handle_event(self, event: Event) -> None:
        for client in self._clients:
            try:
                asyncio.run(self.send_event(client, event))
            except Exception:  # noqa
                logger.error("Could not send event to client")

    @staticmethod
    def serialize_event(event: Event) -> dict:
        return {
            "type": event.event_type,
            "value": event.value,
            "raw": event.raw,
            "timestamp": event.timestamp,
        }

    async def connect_client(self, websocket):
        logger.info("Connecting client")
        self._clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self._clients.remove(websocket)
            logger.info("Disconnected client")

    async def start(self):
        loop = asyncio.get_running_loop()
        self._stop = loop.create_future()

        loop.add_signal_handler(signal.SIGTERM, self._stop.set_result, None)

        async with websockets.serve(self.connect_client, self._host, self._port):
            await self._stop

    async def stop(self):
        self._stop.set_result(None)
