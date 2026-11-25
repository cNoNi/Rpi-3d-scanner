"""Stepper motor driven by a TMC2209 in STEP/DIR mode."""

import threading
from contextlib import contextmanager
from time import sleep

from gpiozero import OutputDevice


class StepperMotor:
    """Moves a stepper motor and tracks its position in microsteps.

    The position is purely software-tracked (no endstop), relative to where
    the motor was when the program started.
    """

    def __init__(self, step_pin, dir_pin, enable_pin, step_delay, pin_factory=None):
        if step_delay <= 0:
            raise ValueError("step_delay must be positive")

        # EN is active-low on the TMC2209. With active_high=False and
        # initial_value=False the pin starts HIGH, so the driver is disabled
        # from the very first moment and never twitches on startup.
        self._enable = OutputDevice(
            enable_pin, active_high=False, initial_value=False, pin_factory=pin_factory
        )
        self._step = OutputDevice(step_pin, initial_value=False, pin_factory=pin_factory)
        self._dir = OutputDevice(dir_pin, initial_value=False, pin_factory=pin_factory)

        self.step_delay = step_delay
        self._position = 0
        self._lock = threading.RLock()

    @property
    def position(self):
        return self._position

    @property
    def is_enabled(self):
        return bool(self._enable.value)

    def set_enabled(self, enabled):
        with self._lock:
            if enabled:
                self._enable.on()
            else:
                self._enable.off()

    @contextmanager
    def enabled(self):
        """Keep the driver powered for the duration of the block."""
        with self._lock:
            self.set_enabled(True)
            try:
                yield self
            finally:
                self.set_enabled(False)

    def move_to(self, target, should_stop=None):
        """Move to an absolute position (in microsteps).

        ``should_stop`` is an optional callable checked between steps; when it
        returns True the move is aborted and the position stays accurate.
        Returns True if the target was reached.
        """
        target = int(target)
        with self._lock:
            if target == self._position:
                return True

            direction = 1 if target > self._position else -1
            if direction > 0:
                self._dir.on()
            else:
                self._dir.off()

            while self._position != target:
                if should_stop is not None and should_stop():
                    return False
                self._step.on()
                sleep(self.step_delay)
                self._step.off()
                sleep(self.step_delay)
                self._position += direction
            return True

    def move_by(self, delta, should_stop=None):
        with self._lock:
            return self.move_to(self._position + int(delta), should_stop)

    def close(self):
        with self._lock:
            self.set_enabled(False)
            for device in (self._enable, self._step, self._dir):
                device.close()
