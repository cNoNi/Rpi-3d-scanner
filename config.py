"""
3D Scanner configuration
"""

# -------------------------
# Motor configuration
# -------------------------

MOTOR_STEP_PIN = 16
MOTOR_DIR_PIN = 20
MOTOR_ENABLE_PIN = 21

# 200 steps/revolution motor(1.8 degree per step)
MOTOR_STEPS_PER_REVOLUTION = 200
# Microstepping resolution e.i. MOTOR_STEPS_PER_REVOLUTION * MOTOR_RESOLUTION = number of microsteps for full revolution 
MOTOR_RESOLUTION = 1

# delay between GPIO pulses
# lower = faster
MOTOR_STEP_DELAY = 0.001


# -------------------------
# Scanner configuration
# -------------------------

PHOTOS_PER_REVOLUTION = 100

# seconds to wait after moving
# for turntable vibrations to stop
PRE_CAPTURE_DELAY = 2

# seconds to wait after photo
# before next movement
POST_CAPTURE_DELAY = 2

# -------------------------
# Camera configuration
# -------------------------

IMAGE_DIRECTORY = "photos"

# -------------------------
# Web server
# -------------------------

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5000