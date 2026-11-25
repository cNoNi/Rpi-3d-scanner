import json
import unittest

from app import create_app
from controllers.scanner import Scanner
from events import EventHub
from tests.fakes import FakeCamera, FakeMotor

HEADERS = {"X-Requested-With": "test"}


class AppTest(unittest.TestCase):
    def setUp(self):
        self.camera = FakeCamera()
        self.motor = FakeMotor()
        self.scanner = Scanner(self.motor, self.camera, 4, 1600, 0, 0)
        self.hub = EventHub(max_clients=1)
        app = create_app(self.scanner, self.camera, self.hub, jog_steps=10)
        self.client = app.test_client()

    def test_post_without_csrf_header_rejected(self):
        response = self.client.post("/motor/cw")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.motor.position, 0)

    def test_jog(self):
        self.assertEqual(self.client.post("/motor/cw", headers=HEADERS).status_code, 200)
        self.client.post("/motor/ccw", headers=HEADERS)
        self.client.post("/motor/ccw", headers=HEADERS)
        self.assertEqual(self.motor.position, -10)

    def test_start_requires_phone(self):
        self.camera.connected = False
        response = self.client.post("/scan/start", headers=HEADERS)
        self.assertEqual(response.status_code, 409)

    def test_start_scan(self):
        response = self.client.post("/scan/start", headers=HEADERS)
        self.assertEqual(response.status_code, 200)
        self.scanner._thread.join(5)
        self.assertEqual(len(self.camera.photos), 4)

    def test_status(self):
        data = self.client.get("/scan/status").get_json()
        self.assertTrue(data["phone_connected"])
        self.assertEqual(data["total"], 4)

    def test_events_client_limit(self):
        first = self.client.get("/events", buffered=False)
        self.assertEqual(first.status_code, 200)
        frame = next(first.response)
        self.assertTrue(frame.startswith(b"data: "))
        self.assertIn("running", json.loads(frame[6:]))
        self.assertEqual(self.client.get("/events").status_code, 503)
        first.close()
        self.assertEqual(len(self.hub._clients), 0)


if __name__ == "__main__":
    unittest.main()
