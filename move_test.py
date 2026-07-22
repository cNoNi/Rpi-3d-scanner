from controlers.motor import Motor
from time import sleep


motor = Motor()

motor.set_motor_enabled(True)

motor.run_to_position_steps(200)

sleep(1)

motor.run_to_position_steps(0)

motor.set_motor_enabled(False)
