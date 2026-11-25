"""3D scanner configuration."""

import os

# ---------------------------------------------------------------------------
# Motor (TMC2209 in STEP/DIR mode, BCM pin numbers)
# ---------------------------------------------------------------------------

MOTOR_STEP_PIN = 16
MOTOR_DIR_PIN = 20
MOTOR_ENABLE_PIN = 26

# Full steps per revolution of the motor (200 = 1.8 degrees per step).
MOTOR_STEPS_PER_REVOLUTION = 200

# Microstepping set in hardware on the driver (MS1/MS2 pins).
# Microsteps per revolution = MOTOR_STEPS_PER_REVOLUTION * MOTOR_MICROSTEPS.
MOTOR_MICROSTEPS = 8

# Half-period of a STEP pulse in seconds. Lower = faster.
MOTOR_STEP_DELAY = 0.001

# Microsteps per single "Rotate CW/CCW" click in the web UI.
MOTOR_JOG_STEPS = 10

# ---------------------------------------------------------------------------
# Scan
# ---------------------------------------------------------------------------

PHOTOS_PER_REVOLUTION = 50

# Seconds to wait after a move so turntable vibrations settle.
PRE_CAPTURE_DELAY = 3.0

# Seconds to wait after a photo before the next move.
POST_CAPTURE_DELAY = 2.0

# ---------------------------------------------------------------------------
# Phone camera
# ---------------------------------------------------------------------------

# Seconds to wait for the "take_photo" command to be sent to the phone.
CAMERA_SEND_TIMEOUT = 5.0

# Seconds to wait for the phone to answer "photo_taken".
CAMERA_CONFIRM_TIMEOUT = 10.0

# ---------------------------------------------------------------------------
# Network
# ---------------------------------------------------------------------------

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5000
WEBSOCKET_PORT = 8765

# Shared secret the phone must pass as ws://<host>:8765/?token=<value>.
# Without it anyone on the network can take over the camera connection.
# Leave unset (empty) to disable the check.
WEBSOCKET_TOKEN = os.environ.get("SCANNER_WS_TOKEN", "")

# Maximum number of browsers listening to live status at the same time.
# Every listener holds one server thread.
MAX_EVENT_CLIENTS = 8
