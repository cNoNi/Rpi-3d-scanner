import config

from queue import Queue
import json
from flask import Flask, jsonify, render_template, Response
from threading import Thread

from controlers.camera import Camera
from controlers.scanner import Scanner

from tmc_driver import Tmc2209, TmcEnableControlPin,TmcMotionControlStepDir, Board, tmc_gpio
from tmc_driver.com import TmcComUart

app = Flask(__name__)

clients = []


camera = Camera(
    image_dir=config.IMAGE_DIRECTORY
)

UART_PORT = {
    Board.RASPBERRY_PI: "/dev/serial0",
    Board.RASPBERRY_PI5: "/dev/ttyAMA0",
    Board.NVIDIA_JETSON: "/dev/ttyTHS1",
}

tmc = Tmc2209(
    TmcEnableControlPin(config.MOTOR_ENABLE_PIN), 
    TmcMotionControlStepDir(config.MOTOR_STEP_PIN,config.MOTOR_DIR_PIN),
    TmcComUart(UART_PORT.get(tmc_gpio.BOARD, "/dev/serial0"))
)

def broadcast(status):
    dead = []

    for client in clients:
        try:
            client.put_nowait(status)
        except:
            dead.append(client)

    for client in dead:
        clients.remove(client)


scanner = Scanner(
    motor=tmc,
    camera=camera,
    photos_per_revolution=config.PHOTOS_PER_REVOLUTION,
    pre_wait=config.PRE_CAPTURE_DELAY,
    post_wait=config.POST_CAPTURE_DELAY,
    on_status_change=broadcast
)



@app.route("/")
def index():
    return render_template("index.html")



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



@app.route("/camera/photo", methods=["POST"])
def take_photo():

    filename = camera.take_photo()

    return jsonify({
        "photo": str(filename)
    })



@app.route("/events")
def events():

    q = Queue()
    clients.append(q)

    q.put(scanner.status())

    def stream():
        try:
            while True:
                data = q.get()
                yield f"data: {json.dumps(data)}\n\n"
        finally:
            if q in clients:
                clients.remove(q)

    return Response(
        stream(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
