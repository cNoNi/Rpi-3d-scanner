import threading
from time import sleep


class Scanner:

    def __init__(
        self,
        motor,
        camera=None,
        photos_per_revolution=100,
        pre_wait=2,
        post_wait=0,
        on_status_change=None,
        steps_per_revolution=200,
        resolution=8,
    ):

        self.motor = motor
        self.camera = camera

        self.photos_per_revolution = photos_per_revolution
        self.steps_per_revolution = steps_per_revolution
        self.resolution = resolution

        self.microsteps_per_revolution = (
            steps_per_revolution * resolution
        )

        self.pre_wait = pre_wait
        self.post_wait = post_wait

        self.running = False
        self.current_photo = 0

        self.on_status_change = on_status_change

        self._lock = threading.Lock()
        self.error = None



    def notify(self):

        if self.on_status_change:
            self.on_status_change(
                self.status()
            )



    def motor_setup(self):

        self.motor.set_motor_enabled(True)

        self.motor.run_to_position_steps(
            0
        )

        self.motor.set_microstepping_resolution(
            self.resolution
        )



    def start(self):
        if self.camera is None:
            raise RuntimeError("Brak kamery")

        if not self._lock.acquire(blocking=False):
            return  # skan już trwa

        self.running = True
        self.current_photo = 0
        self.error = None
        self.notify()

        try:
            self.motor_setup()

            step_per_photo = (
                self.microsteps_per_revolution /
                self.photos_per_revolution
            )

            for photo in range(self.photos_per_revolution):
                if not self.running:
                    break

                sleep(self.pre_wait)

                if not self.running:
                    break

                self.camera.take_photo(f"image_{photo:04d}.jpg")
                sleep(self.post_wait)

                self.current_photo = photo + 1
                self.notify()

                if photo == self.photos_per_revolution - 1:
                    break

                self.motor.run_to_position_steps(
                    round((photo + 1) * step_per_photo)
                )

        except Exception as e:
            self.error = str(e)
            raise
        finally:
            self.running = False
            self.motor.set_motor_enabled(False)
            self.notify()
            self._lock.release()


    def stop(self):
        self.running = False  # reszta posprząta w finally


    def status(self):
        return {
            "running": self.running,
            "photo": self.current_photo,
            "total": self.photos_per_revolution,
            "error": self.error,
        }