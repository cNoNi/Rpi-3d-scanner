import unittest

from gpiozero.pins.mock import MockFactory

from controllers.motor import StepperMotor


class StepperMotorTest(unittest.TestCase):
    def setUp(self):
        self.factory = MockFactory()
        self.motor = StepperMotor(16, 20, 26, step_delay=1e-6, pin_factory=self.factory)

    def tearDown(self):
        self.motor.close()

    def test_driver_disabled_on_start(self):
        # EN is active-low: HIGH means disabled.
        self.assertTrue(self.factory.pin(26).state)
        self.assertFalse(self.motor.is_enabled)

    def test_enabled_context_restores_disabled(self):
        with self.motor.enabled():
            self.assertFalse(self.factory.pin(26).state)
        self.assertTrue(self.factory.pin(26).state)

    def test_moves_and_tracks_position(self):
        self.assertTrue(self.motor.move_to(5))
        self.assertEqual(self.motor.position, 5)
        self.assertTrue(self.factory.pin(20).state)
        self.motor.move_by(-8)
        self.assertEqual(self.motor.position, -3)
        self.assertFalse(self.factory.pin(20).state)

    def test_stop_keeps_position_accurate(self):
        calls = []

        def stop_after_three():
            calls.append(1)
            return len(calls) > 3

        self.assertFalse(self.motor.move_to(100, should_stop=stop_after_three))
        self.assertEqual(self.motor.position, 3)

    def test_rejects_bad_delay(self):
        with self.assertRaises(ValueError):
            StepperMotor(5, 6, 7, step_delay=0, pin_factory=self.factory)


if __name__ == "__main__":
    unittest.main()
