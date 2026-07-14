import config

from queue import Queue
import json
from flask import Flask, jsonify, render_template, Response
from threading import Thread

from controlers.camera import Camera
from controlers.motor import StepperMotor
from controlers.scanner import Scanner


app = Flask(__name__)

clients = []
# -------------------------
# Hardware initialization
# -------------------------

camera = Camera(
    image_dir=config.IMAGE_DIRECTORY
)


motor = StepperMotor(
    step_pin=config.MOTOR_STEP_PIN,
    dir_pin=config.MOTOR_DIR_PIN,
    enable_pin=config.MOTOR_ENABLE_PIN,
    steps_per_revolution=config.MOTOR_STEPS_PER_REVOLUTION,
    step_delay=config.MOTOR_STEP_DELAY
)

scanner = Scanner(
    motor=motor,
    camera=camera,
    photos_per_revolution=config.PHOTOS_PER_REVOLUTION,
    pre_wait=config.PRE_CAPTURE_DELAY,
    post_wait=config.POST_CAPTURE_DELAY
)



# -------------------------
# Web interface
# -------------------------

@app.route("/")
def index():
    return render_template("index.html")



# -------------------------
# Scanner control
# -------------------------

@app.route("/scan/start", methods=["POST"])
def start_scan():

    if scanner.running:
        return jsonify({
            "status": "already running"
        })


    thread = Thread(
        target=scanner.start
    )

    thread.daemon = True
    thread.start()


    return jsonify({
        "status": "started"
    })



@app.route("/scan/stop", methods=["POST"])
def stop_scan():

    scanner.stop()

    return jsonify({
        "status": "stopping"
    })



@app.route("/scan/status")
def scan_status():

    return jsonify(
        scanner.status()
    )



# -------------------------
# Camera control
# -------------------------

@app.route("/camera/photo", methods=["POST"])
def take_photo():

    filename = camera.take_photo()

    return jsonify({
        "photo": str(filename)
    })



# -------------------------
# Manual motor control
# -------------------------

@app.route("/motor/cw", methods=["POST"])
def motor_cw():

    motor.rotate_steps(
        100,
        clockwise=True
    )

    return jsonify({
        "status": "CW moved"
    })



@app.route("/motor/ccw", methods=["POST"])
def motor_ccw():

    motor.rotate_steps(
        100,
        clockwise=False
    )

    return jsonify({
        "status": "CCW moved"
    })


@app.route("/events")
def events():

    q = Queue()
    clients.append(q)

    def stream():
        try:
            while True:
                data = q.get()
                yield f"data: {json.dumps(data)}\n\n"
        finally:
            clients.remove(q)

    return Response(
        stream(),
        mimetype="text/event-stream"
    )


# -------------------------
# Start server
# -------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )