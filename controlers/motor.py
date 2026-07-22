from time import sleep
from gpiozero import OutputDevice


class Motor:

    def __init__(
        self,
        en_pin=26,
        step_pin=16,
        dir_pin=20,
        step_delay=0.002
    ):

        # TMC2209:
        # EN LOW  = silnik włączony
        # EN HIGH = silnik wyłączony

        self.en = OutputDevice(
            en_pin,
            active_high=True
        )

        self.step = OutputDevice(
            step_pin,
            active_high=True
        )

        self.dir = OutputDevice(
            dir_pin,
            active_high=True
        )


        self.step_delay = step_delay

        self.position = 0

        # start: wyłączony sterownik
        self.set_motor_enabled(False)



    def set_motor_enabled(self, enabled):

        if enabled:
            # EN = LOW
            self.en.off()

        else:
            # EN = HIGH
            self.en.on()



    def set_microstepping_resolution(self, resolution):

        # TMC2209 ustawiony sprzętowo
        # zostawiamy dla zgodności ze Scanner

        self.resolution = resolution



    def run_to_position_steps(self, target):

        target = int(target)

        if target == self.position:
            return


        if target > self.position:

            self.dir.on()

            steps = target - self.position


        else:

            self.dir.off()

            steps = self.position - target



        for _ in range(steps):

            self.step.on()

            sleep(self.step_delay)

            self.step.off()

            sleep(self.step_delay)



        self.position = target



    def close(self):

        self.set_motor_enabled(False)

        self.en.close()
        self.step.close()
        self.dir.close()
