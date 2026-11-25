"""Turntable scan: rotate, settle, take photo, repeat.

The scanner owns the motor and the camera: scans, jogs and single photos all
go through one lock, so they can never run at the same time.
"""

import logging
import threading

log = logging.getLogger(__name__)


class Scanner:
    def __init__(
        self,
        motor,
        camera,
        photos_per_revolution,
        microsteps_per_revolution,
        pre_capture_delay=2.0,
        post_capture_delay=0.0,
        on_status_change=None,
    ):
        if photos_per_revolution <= 0:
            raise ValueError("photos_per_revolution must be positive")
        if microsteps_per_revolution < photos_per_revolution:
            raise ValueError("more photos per revolution than microsteps per revolution")
        if pre_capture_delay < 0 or post_capture_delay < 0:
            raise ValueError("delays must not be negative")

        self.motor = motor
        self.camera = camera
        self.photos_per_revolution = photos_per_revolution
        self.microsteps_per_revolution = microsteps_per_revolution
        self.pre_capture_delay = pre_capture_delay
        self.post_capture_delay = post_capture_delay
        self.on_status_change = on_status_change

        self._busy = threading.Lock()
        self._stop = threading.Event()
        self._thread = None

        self._scanning = False
        self._current_photo = 0
        self._error = None

    # -- state ---------------------------------------------------------------

    @property
    def busy(self):
        return self._busy.locked()

    @property
    def scanning(self):
        return self._scanning

    def status(self):
        return {
            "running": self._scanning,
            "stopping": self._scanning and self._stop.is_set(),
            "busy": self.busy,
            "photo": self._current_photo,
            "total": self.photos_per_revolution,
            "error": self._error,
        }

    def _notify(self):
        if self.on_status_change is not None:
            try:
                self.on_status_change()
            except Exception:
                log.exception("Status callback failed")

    # -- scan ----------------------------------------------------------------

    def start(self):
        """Start a scan in the background. Returns False if something is already running."""
        if not self._busy.acquire(blocking=False):
            return False
        try:
            self._stop.clear()
            self._scanning = True
            self._current_photo = 0
            self._error = None
            self._thread = threading.Thread(target=self._run, name="scan", daemon=True)
            self._thread.start()
        except BaseException:
            self._scanning = False
            self._busy.release()
            raise
        self._notify()
        return True

    def stop(self):
        if self._scanning:
            self._stop.set()
            self._notify()

    def shutdown(self, timeout=5.0):
        """Stop the scan (if any) and wait for it to finish."""
        self._stop.set()
        thread = self._thread
        if thread is not None:
            thread.join(timeout)

    def _run(self):
        try:
            with self.motor.enabled():
                origin = self.motor.position
                for index in range(self.photos_per_revolution):
                    if index > 0:
                        target = origin + round(
                            index * self.microsteps_per_revolution / self.photos_per_revolution
                        )
                        if not self.motor.move_to(target, should_stop=self._stop.is_set):
                            break

                    if self._stop.wait(self.pre_capture_delay):
                        break

                    self.camera.take_photo(f"image_{index:04d}.jpg")
                    self._current_photo = index + 1
                    self._notify()

                    if self._stop.wait(self.post_capture_delay):
                        break
        except Exception as exc:
            log.exception("Scan failed")
            self._error = str(exc)
        finally:
            self._scanning = False
            self._busy.release()
            self._notify()

    # -- manual control ------------------------------------------------------

    def jog(self, steps):
        """Rotate by ``steps`` microsteps. Returns False if the scanner is busy."""
        if not self._busy.acquire(blocking=False):
            return False
        try:
            with self.motor.enabled():
                self.motor.move_by(steps)
        finally:
            self._busy.release()
        return True

    def take_single_photo(self):
        """Take one photo. Returns False if the scanner is busy."""
        if not self._busy.acquire(blocking=False):
            return False
        self._notify()
        try:
            self.camera.take_photo("manual.jpg")
        finally:
            self._busy.release()
            self._notify()
        return True
