"""Hardware check: spin the motor continuously until Ctrl+C.

Run on the Raspberry Pi from the repository root:
    python -m scripts.spin_motor
"""

import config
from controllers.motor import StepperMotor

STEPS_PER_SECOND = 400


def main():
    motor = StepperMotor(
        step_pin=config.MOTOR_STEP_PIN,
        dir_pin=config.MOTOR_DIR_PIN,
        enable_pin=config.MOTOR_ENABLE_PIN,
        step_delay=1 / (STEPS_PER_SECOND * 2),
    )
    print("Spinning, press Ctrl+C to stop")
    try:
        with motor.enabled():
            while True:
                motor.move_by(STEPS_PER_SECOND)
    except KeyboardInterrupt:
        pass
    finally:
        motor.close()


if __name__ == "__main__":
    main()
