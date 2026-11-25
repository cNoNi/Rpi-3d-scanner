import asyncio
import socket
import time
import unittest

from websockets.asyncio.client import connect
from websockets.exceptions import InvalidStatus

from controllers.camera import PhoneCamera
from controllers.phone_server import start_phone_server


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class PhoneServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camera = PhoneCamera()
        cls.port = free_port()
        start_phone_server(cls.camera, "127.0.0.1", cls.port, token="secret")
        time.sleep(0.5)

    def test_bad_token_rejected(self):
        async def attempt():
            async with connect(f"ws://127.0.0.1:{self.port}/?token=wrong"):
                pass

        with self.assertRaises(InvalidStatus):
            asyncio.run(attempt())
        self.assertFalse(self.camera.connected)

    def test_good_token_connects(self):
        async def attempt():
            async with connect(f"ws://127.0.0.1:{self.port}/?token=secret"):
                for _ in range(50):
                    if self.camera.connected:
                        return True
                    await asyncio.sleep(0.01)
                return False

        self.assertTrue(asyncio.run(attempt()))


if __name__ == "__main__":
    unittest.main()
