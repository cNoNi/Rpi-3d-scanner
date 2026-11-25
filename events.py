"""Fan-out of status updates to Server-Sent Events listeners."""

import json
import queue
import threading

HEARTBEAT_INTERVAL = 15.0


class EventHub:
    """Thread-safe publish/subscribe with bounded per-client queues.

    Only the newest status matters, so a slow client drops old messages
    instead of growing its queue without limit.
    """

    def __init__(self, max_clients, queue_size=8):
        self.max_clients = max_clients
        self.queue_size = queue_size
        self._clients = set()
        self._lock = threading.Lock()

    def subscribe(self):
        """Return a new queue, or None if the client limit is reached."""
        with self._lock:
            if len(self._clients) >= self.max_clients:
                return None
            client = queue.Queue(maxsize=self.queue_size)
            self._clients.add(client)
            return client

    def unsubscribe(self, client):
        with self._lock:
            self._clients.discard(client)

    def publish(self, data):
        with self._lock:
            clients = list(self._clients)
        for client in clients:
            _put_latest(client, data)

    def stream(self, client, initial=None):
        """Generator of SSE frames for one client; unsubscribes when closed."""
        try:
            if initial is not None:
                yield _format(initial)
            while True:
                try:
                    data = client.get(timeout=HEARTBEAT_INTERVAL)
                except queue.Empty:
                    # A comment line keeps proxies happy and lets the server
                    # notice disconnected clients and free their thread.
                    yield ": keepalive\n\n"
                    continue
                yield _format(data)
        finally:
            self.unsubscribe(client)


def _put_latest(client, data):
    while True:
        try:
            client.put_nowait(data)
            return
        except queue.Full:
            try:
                client.get_nowait()
            except queue.Empty:
                pass


def _format(data):
    return f"data: {json.dumps(data)}\n\n"
