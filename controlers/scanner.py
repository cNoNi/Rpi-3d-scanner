from time import sleep


class Scanner:
    """
    Controls the scanning sequence.

    Sequence:
        1. Move turntable
        2. Wait for vibrations to stop
        3. Take photo
        4. Wait for camera
        5. Repeat
    """

    def __init__(
        self,
        motor,
        camera,
        photos_per_revolution=100,
        pre_wait=2,
        post_wait=2
    ):

        self.motor = motor
        self.camera = camera

        self.photos_per_revolution = photos_per_revolution

        self.pre_wait = pre_wait
        self.post_wait = post_wait

        self.running = False
        self.current_photo = 0


    def start(self):
        """
        Start complete scan.
        """

        if self.running:
            return

        self.running = True
        self.current_photo = 0

        total_steps = (
            self.motor.steps_per_revolution
            //
            self.photos_per_revolution
        )


        try:

            while self.running and (
                self.current_photo < self.photos_per_revolution
            ):

                # move platform
                self.motor.rotate_steps(
                    total_steps,
                    clockwise=True
                )


                # allow object to settle
                sleep(self.pre_wait)


                # capture image
                filename = (
                    f"image_{self.current_photo:04d}.jpg"
                )

                self.camera.take_photo(filename)


                # allow camera to finish
                sleep(self.post_wait)


                self.current_photo += 1


        finally:
            self.running = False



    def stop(self):
        """
        Stop scan after current operation.
        """

        self.running = False



    def status(self):
        """
        Return current scan status.
        """

        return {
            "running": self.running,
            "photo": self.current_photo,
            "total": self.photos_per_revolution
        }