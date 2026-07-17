"""
3D Scanner configuration
"""

# -------------------------
# Motor configuration
# -------------------------

MOTOR_STEP_PIN = 17
MOTOR_DIR_PIN = 27
MOTOR_ENABLE_PIN = 4

MOTOR_MS1 = 22
MOTOR_MS2 = 23
MOTOR_MS3 = 24
# 200 steps/revolution motor
# multiplied by Big Easy Driver microstepping
# Example: 200 * 64 = 12800
MOTOR_STEPS_PER_REVOLUTION = 3200

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