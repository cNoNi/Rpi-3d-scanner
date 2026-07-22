from time import sleep

from gpiozero import OutputDevice


class Motor:
    def __init__(
        self,
        en_pin=26,
        step_pin=16,
        dir_pin=20,
        step_delay=0.001,
    ):
        """
        step_delay - czas pomiędzy zmianami stanu STEP.
        0.001 s daje ok. 500 kroków/s.
        """

        self.enable = OutputDevice(en_pin, active_high=True, initial_value=True)
        self.step = OutputDevice(step_pin, initial_value=False)
        self.dir = OutputDevice(dir_pin, initial_value=False)

        self.step_delay = step_delay
        self.position = 0

    def set_motor_enabled(self, enabled: bool):
        if enabled:
            self.enable.off()
        else:
            self.enable.on()

    def set_microstepping_resolution(self, resolution):
        # Rozdzielczość ustawiana sprzętowo.
        pass

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