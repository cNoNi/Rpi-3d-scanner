import asyncio
import threading
import unittest

from controllers.camera import CameraError, PhoneCamera


class FakeWebSocket:
    def __init__(self, on_send=None):
        self.sent = []
        self.on_send = on_send

    async def send(self, message):
        self.sent.append(message)
        if self.on_send:
            self.on_send()


class CameraTest(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.loop.run_forever, daemon=True)
        self.thread.start()
        self.camera = PhoneCamera(send_timeout=1, confirm_timeout=0.2)

    def tearDown(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join(2)
        self.loop.close()

    def test_not_connected(self):
        with self.assertRaises(CameraError):
            self.camera.take_photo()

    def test_photo_confirmed(self):
        ws = FakeWebSocket(on_send=self.camera.confirm)
        self.camera.attach(ws, self.loop)
        self.camera.take_photo()
        self.assertEqual(ws.sent, ["take_photo"])

    def test_timeout_without_confirmation(self):
        self.camera.attach(FakeWebSocket(), self.loop)
        with self.assertRaises(CameraError):
            self.camera.take_photo()

    def test_stale_confirmation_is_ignored(self):
        self.camera.attach(FakeWebSocket(), self.loop)
        self.camera.confirm()  # nothing pending
        with self.assertRaises(CameraError):
            self.camera.take_photo()

    def test_detach_only_active_connection(self):
        old, new = FakeWebSocket(), FakeWebSocket()
        self.camera.attach(old, self.loop)
        self.assertIs(self.camera.attach(new, self.loop), old)
        self.camera.detach(old)
        self.assertTrue(self.camera.connected)
        self.camera.detach(new)
        self.assertFalse(self.camera.connected)


if __name__ == "__main__":
    unittest.main()
