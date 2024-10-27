import asyncio

from waterrower_websocket_server.rower import Rower
from waterrower_websocket_server.server import WaterrowerWebsocketServer


def main():
    rower = Rower()
    server = WaterrowerWebsocketServer(rower, host="localhost", port=9899)

    rower.open()
    rower.reset_request()
    asyncio.run(server.start())


if __name__ == "__main__":
    main()
