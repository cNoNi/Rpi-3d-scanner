"""Hardware check: move forward by one full revolution and back.

Run on the Raspberry Pi from the repository root:
    python -m scripts.move_motor
"""

from time import sleep

import config
from controllers.motor import StepperMotor


def main():
    motor = StepperMotor(
        step_pin=config.MOTOR_STEP_PIN,
        dir_pin=config.MOTOR_DIR_PIN,
        enable_pin=config.MOTOR_ENABLE_PIN,
        step_delay=config.MOTOR_STEP_DELAY,
    )
    revolution = config.MOTOR_STEPS_PER_REVOLUTION * config.MOTOR_MICROSTEPS
    try:
        with motor.enabled():
            motor.move_to(revolution)
            sleep(1)
            motor.move_to(0)
    finally:
        motor.close()


if __name__ == "__main__":
    main()
