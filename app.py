"""Web UI and HTTP API of the 3D scanner."""

import atexit
import logging

from flask import Flask, Response, jsonify, render_template, request

import config
from controllers.camera import CameraError
from events import EventHub

log = logging.getLogger(__name__)

# Browsers only send custom headers cross-origin after a CORS preflight, which
# this server never approves. Requiring one blocks CSRF from other websites.
CSRF_HEADER = "X-Requested-With"


def snapshot(scanner, camera):
    """Current state sent to the web UI."""
    return {**scanner.status(), "phone_connected": camera.connected}


def create_app(scanner, camera, hub, jog_steps):
    app = Flask(__name__)

    def status():
        return snapshot(scanner, camera)

    def error(message, code):
        return jsonify(status="error", message=message), code

    @app.before_request
    def require_csrf_header():
        if request.method == "POST" and not request.headers.get(CSRF_HEADER):
            return error("missing request header", 403)
        return None

    @app.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        return response

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/scan/status")
    def scan_status():
        return jsonify(status())

    @app.post("/scan/start")
    def start_scan():
        if not camera.connected:
            return error("phone is not connected", 409)
        if not scanner.start():
            return error("scanner is busy", 409)
        return jsonify(status="started")

    @app.post("/scan/stop")
    def stop_scan():
        scanner.stop()
        return jsonify(status="stopping")

    @app.post("/camera/photo")
    def take_photo():
        try:
            if not scanner.take_single_photo():
                return error("scanner is busy", 409)
        except CameraError as exc:
            return error(str(exc), 503)
        return jsonify(status="photo_taken")

    def jog(direction):
        if not scanner.jog(direction * jog_steps):
            return error("scanner is busy", 409)
        return jsonify(status="ok")

    @app.post("/motor/cw")
    def motor_cw():
        return jog(1)

    @app.post("/motor/ccw")
    def motor_ccw():
        return jog(-1)

    @app.get("/events")
    def events():
        client = hub.subscribe()
        if client is None:
            return error("too many listeners", 503)
        return Response(
            hub.stream(client, initial=status()),
            mimetype="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    return app


def main():
    # Hardware imports live here so the rest of the module can be imported
    # (and tested) on machines without GPIO.
    from controllers.camera import PhoneCamera
    from controllers.motor import StepperMotor
    from controllers.phone_server import start_phone_server
    from controllers.scanner import Scanner

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    hub = EventHub(max_clients=config.MAX_EVENT_CLIENTS)

    def publish_status():
        # Looked up at call time: both objects exist before anything publishes.
        hub.publish(snapshot(scanner, camera))

    camera = PhoneCamera(
        send_timeout=config.CAMERA_SEND_TIMEOUT,
        confirm_timeout=config.CAMERA_CONFIRM_TIMEOUT,
        on_change=publish_status,
    )
    motor = StepperMotor(
        step_pin=config.MOTOR_STEP_PIN,
        dir_pin=config.MOTOR_DIR_PIN,
        enable_pin=config.MOTOR_ENABLE_PIN,
        step_delay=config.MOTOR_STEP_DELAY,
    )
    scanner = Scanner(
        motor=motor,
        camera=camera,
        photos_per_revolution=config.PHOTOS_PER_REVOLUTION,
        microsteps_per_revolution=config.MOTOR_STEPS_PER_REVOLUTION * config.MOTOR_MICROSTEPS,
        pre_capture_delay=config.PRE_CAPTURE_DELAY,
        post_capture_delay=config.POST_CAPTURE_DELAY,
        on_status_change=publish_status,
    )

    def shutdown():
        scanner.shutdown()
        motor.close()

    atexit.register(shutdown)

    app = create_app(scanner, camera, hub, jog_steps=config.MOTOR_JOG_STEPS)
    start_phone_server(camera, config.SERVER_HOST, config.WEBSOCKET_PORT, config.WEBSOCKET_TOKEN)
    app.run(host=config.SERVER_HOST, port=config.SERVER_PORT, debug=False, threaded=True)


if __name__ == "__main__":
    main()
