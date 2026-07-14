from gpiozero import OutputDevice
from time import sleep


class MotorError(Exception):
    pass


class StepperMotor:
    """
    Control a stepper motor through Big Easy Driver.

    Connections:
        STEP -> GPIO step_pin
        DIR  -> GPIO dir_pin
        EN   -> GPIO enable_pin
    """

    def __init__(
        self,
        step_pin=20,
        dir_pin=21,
        enable_pin=19,
        steps_per_revolution=200*64,
        step_delay=0.001
    ):

        self.step_pin = OutputDevice(step_pin)
        self.dir_pin = OutputDevice(dir_pin)
        self.enable_pin = OutputDevice(enable_pin)

        self.steps_per_revolution = steps_per_revolution
        self.step_delay = step_delay

        # Start disabled
        self.disable()


    def enable(self):
        """
        Enable Big Easy Driver.
        """
        self.enable_pin.off()


    def disable(self):
        """
        Disable Big Easy Driver.
        """
        self.enable_pin.on()


    def set_direction(self, clockwise=True):
        """
        Set motor direction.
        """

        if clockwise:
            self.dir_pin.on()
        else:
            self.dir_pin.off()


    def step(self):
        """
        Generate one step pulse.
        """

        self.step_pin.on()
        sleep(self.step_delay)

        self.step_pin.off()
        sleep(self.step_delay)


    def rotate_steps(self, steps, clockwise=True):
        """
        Rotate given number of steps.
        """

        if steps < 0:
            clockwise = not clockwise
            steps = abs(steps)

        self.enable()

        self.set_direction(clockwise)

        for _ in range(steps):
            self.step()

        self.disable()


    def rotate_revolution(self, revolutions=1, clockwise=True):
        """
        Rotate full revolution(s).
        """

        steps = int(
            self.steps_per_revolution * revolutions
        )

        self.rotate_steps(
            steps,
            clockwise
        )


    def rotate_angle(self, angle, clockwise=True):
        """
        Rotate by degrees.
        """

        steps = int(
            self.steps_per_revolution *
            angle / 360
        )

        self.rotate_steps(
            steps,
            clockwise
        )