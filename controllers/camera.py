"""Phone used as a remote camera over a WebSocket.

Protocol: the server sends ``take_photo``, the phone answers ``photo_taken``
once the picture is saved on the phone.
"""

import asyncio
import logging
import threading

log = logging.getLogger(__name__)


class CameraError(RuntimeError):
    pass


class PhoneCamera:
    def __init__(self, send_timeout=5.0, confirm_timeout=10.0, on_change=None):
        self.send_timeout = send_timeout
        self.confirm_timeout = confirm_timeout
        self.on_change = on_change

        self._state_lock = threading.Lock()
        self._capture_lock = threading.Lock()
        self._websocket = None
        self._loop = None

        self._confirmed = threading.Event()
        self._pending = False

    @property
    def connected(self):
        return self._websocket is not None

    def attach(self, websocket, loop):
        """Register a new phone connection. Returns the replaced one, if any."""
        with self._state_lock:
            previous = self._websocket
            self._websocket = websocket
            self._loop = loop
        log.info("Phone connected")
        self._notify()
        return previous

    def detach(self, websocket):
        """Forget the connection, but only if it is still the active one."""
        with self._state_lock:
            if self._websocket is not websocket:
                return
            self._websocket = None
            self._loop = None
        log.info("Phone disconnected")
        self._notify()

    def confirm(self):
        """Called when the phone reports ``photo_taken``."""
        with self._state_lock:
            if not self._pending:
                log.warning("Ignoring unexpected photo confirmation")
                return
            self._pending = False
        self._confirmed.set()

    def take_photo(self, name="photo"):
        """Trigger the phone shutter and block until it confirms."""
        if not self._capture_lock.acquire(blocking=False):
            raise CameraError("Camera is busy")
        try:
            with self._state_lock:
                websocket, loop = self._websocket, self._loop
                if websocket is None or loop is None:
                    raise CameraError("Phone is not connected")
                self._confirmed.clear()
                self._pending = True

            try:
                future = asyncio.run_coroutine_threadsafe(websocket.send("take_photo"), loop)
                try:
                    future.result(timeout=self.send_timeout)
                except Exception as exc:
                    future.cancel()
                    raise CameraError(f"Could not send command to phone: {exc}") from exc

                if not self._confirmed.wait(self.confirm_timeout):
                    raise CameraError("Phone did not confirm the photo in time")
            finally:
                with self._state_lock:
                    self._pending = False

            log.info("Photo taken: %s", name)
        finally:
            self._capture_lock.release()

    def _notify(self):
        if self.on_change is not None:
            try:
                self.on_change()
            except Exception:
                log.exception("Camera on_change callback failed")
