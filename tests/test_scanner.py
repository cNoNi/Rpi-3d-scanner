import threading
import unittest

from controllers.scanner import Scanner
from tests.fakes import FakeCamera, FakeMotor


def make_scanner(motor=None, camera=None, photos=4, microsteps=1600, **kwargs):
    return Scanner(
        motor=motor or FakeMotor(),
        camera=camera or FakeCamera(),
        photos_per_revolution=photos,
        microsteps_per_revolution=microsteps,
        pre_capture_delay=0,
        post_capture_delay=0,
        **kwargs,
    )


class ScannerTest(unittest.TestCase):
    def run_scan(self, scanner):
        self.assertTrue(scanner.start())
        scanner._thread.join(5)
        self.assertFalse(scanner.busy)

    def test_full_scan_relative_to_current_position(self):
        motor = FakeMotor(position=100)
        camera = FakeCamera()
        scanner = make_scanner(motor, camera)
        self.run_scan(scanner)
        self.assertEqual(motor.visited, [500, 900, 1300])
        self.assertEqual(len(camera.photos), 4)
        self.assertEqual(scanner.status()["photo"], 4)
        self.assertIsNone(scanner.status()["error"])
        self.assertFalse(motor.enabled_now)

    def test_error_is_reported_and_lock_released(self):
        scanner = make_scanner(camera=FakeCamera(fail_on=2))
        self.run_scan(scanner)
        status = scanner.status()
        self.assertEqual(status["photo"], 2)
        self.assertEqual(status["error"], "camera exploded")
        self.assertFalse(status["running"])

    def test_busy_blocks_jog_photo_and_second_start(self):
        camera = FakeCamera()
        camera.gate = threading.Event()
        scanner = make_scanner(camera=camera)
        self.assertTrue(scanner.start())
        try:
            self.assertFalse(scanner.start())
            self.assertFalse(scanner.jog(10))
            self.assertFalse(scanner.take_single_photo())
        finally:
            scanner.stop()
            camera.gate.set()
            scanner._thread.join(5)
        self.assertTrue(scanner.jog(10))

    def test_stop_ends_scan_early(self):
        camera = FakeCamera()
        camera.gate = threading.Event()
        scanner = make_scanner(camera=camera)
        scanner.start()
        scanner.stop()
        self.assertTrue(scanner.status()["stopping"])
        camera.gate.set()
        scanner._thread.join(5)
        self.assertLessEqual(len(camera.photos), 1)
        self.assertFalse(scanner.status()["running"])

    def test_status_callback_called(self):
        calls = []
        scanner = make_scanner(on_status_change=lambda: calls.append(1))
        self.run_scan(scanner)
        self.assertGreaterEqual(len(calls), 6)

    def test_validation(self):
        with self.assertRaises(ValueError):
            make_scanner(photos=0)
        with self.assertRaises(ValueError):
            make_scanner(photos=100, microsteps=50)


if __name__ == "__main__":
    unittest.main()
