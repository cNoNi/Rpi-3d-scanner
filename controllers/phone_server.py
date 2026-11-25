"""WebSocket server the phone camera connects to."""

import asyncio
import hmac
import logging
import threading
from http import HTTPStatus
from urllib.parse import parse_qs, urlsplit

from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed

log = logging.getLogger(__name__)

# The phone only sends short commands; refuse anything larger.
MAX_MESSAGE_SIZE = 1024


def _token_from_path(path):
    values = parse_qs(urlsplit(path).query).get("token", [])
    return values[0] if values else ""


def _make_request_check(token):
    def process_request(connection, request):
        if token and not hmac.compare_digest(
            _token_from_path(request.path).encode(), token.encode()
        ):
            log.warning("Rejected phone connection from %s: bad token", connection.remote_address)
            return connection.respond(HTTPStatus.FORBIDDEN, "Forbidden\n")
        return None

    return process_request


def _make_handler(camera):
    async def handler(websocket):
        previous = camera.attach(websocket, asyncio.get_running_loop())
        if previous is not None:
            log.info("New phone connection replaces the previous one")
            await previous.close(1000, "replaced by a new connection")
        try:
            async for message in websocket:
                if message == "photo_taken":
                    camera.confirm()
                else:
                    log.warning("Unknown message from phone: %.64r", message)
        except ConnectionClosed:
            pass
        finally:
            camera.detach(websocket)

    return handler


def start_phone_server(camera, host, port, token=""):
    """Run the WebSocket server in a daemon thread."""
    if not token:
        log.warning(
            "SCANNER_WS_TOKEN is not set: anyone on the network can connect as the camera"
        )

    async def main():
        async with serve(
            _make_handler(camera),
            host,
            port,
            process_request=_make_request_check(token),
            max_size=MAX_MESSAGE_SIZE,
        ):
            log.info("Phone WebSocket server listening on %s:%d", host, port)
            await asyncio.Future()

    thread = threading.Thread(target=asyncio.run, args=(main(),), name="phone-ws", daemon=True)
    thread.start()
    return thread
