import config

import json
import asyncio

from queue import Queue
from threading import Thread

from flask import (
    Flask,
    jsonify,
    render_template,
    Response
)

import websockets

from controlers.camera import Camera
from controlers.motor import Motor
from controlers.scanner import Scanner


app = Flask(__name__)


clients = []

phone = None
ws_loop = None



camera = Camera(
    image_dir=config.IMAGE_DIRECTORY
)



motor = Motor(
    en_pin=config.MOTOR_ENABLE_PIN,
    step_pin=config.MOTOR_STEP_PIN,
    dir_pin=config.MOTOR_DIR_PIN
)



def broadcast(status):

    dead = []

    for client in clients:

        try:
            client.put_nowait(status)

        except:
            dead.append(client)


    for client in dead:

        if client in clients:
            clients.remove(client)



async def _send_take_photo():

    if phone is not None:
        await phone.send(
            "take_photo"
        )



def scanner_take_photo(filename):

    if phone is None:
        print("Telefon nie podłączony")
        return


    asyncio.run_coroutine_threadsafe(
        _send_take_photo(),
        ws_loop
    )



scanner = Scanner(

    motor=motor,

    camera=camera,

    photos_per_revolution=
        config.PHOTOS_PER_REVOLUTION,

    pre_wait=
        config.PRE_CAPTURE_DELAY,

    post_wait=
        config.POST_CAPTURE_DELAY,

    on_status_change=
        broadcast,

    take_photo_callback=
        scanner_take_photo
)



@app.route("/")
def index():

    return render_template(
        "index.html"
    )



@app.route(
    "/scan/start",
    methods=["POST"]
)
def start_scan():

    if scanner.running:

        return jsonify({
            "status":
            "already running"
        })


    Thread(
        target=scanner.start,
        daemon=True
    ).start()


    return jsonify({
        "status":
        "started"
    })



@app.route(
    "/scan/stop",
    methods=["POST"]
)
def stop_scan():

    scanner.stop()

    return jsonify({
        "status":
        "stopping"
    })



@app.route(
    "/scan/status"
)
def scan_status():

    return jsonify(
        scanner.status()
    )



@app.route(
    "/camera/photo",
    methods=["POST"]
)
def take_photo():


    if phone is None:

        return jsonify({
            "status":
            "phone_not_connected"
        }),400



    asyncio.run_coroutine_threadsafe(
        _send_take_photo(),
        ws_loop
    )


    return jsonify({
        "status":
        "photo_requested"
    })



@app.route("/events")
def events():

    q = Queue()

    clients.append(q)


    q.put(
        scanner.status()
    )


    def stream():

        try:

            while True:

                data = q.get()

                yield (
                    f"data: "
                    f"{json.dumps(data)}\n\n"
                )


        finally:

            if q in clients:
                clients.remove(q)



    return Response(

        stream(),

        mimetype=
        "text/event-stream",

        headers={

            "Cache-Control":
            "no-cache",

            "Connection":
            "keep-alive",

            "X-Accel-Buffering":
            "no"

        }
    )



async def websocket_handler(websocket):

    global phone

    phone = websocket

    print(
        "Telefon połączony"
    )


    try:

        async for message in websocket:

            print(
                "Telefon:",
                message
            )


    except websockets.ConnectionClosed:

        print(
            "Telefon rozłączony"
        )


    finally:

        phone = None



def websocket_thread():

    global ws_loop


    async def main():

        global ws_loop


        ws_loop = (
            asyncio
            .get_running_loop()
        )


        async with websockets.serve(

            websocket_handler,

            "0.0.0.0",

            8765

        ):

            print(
                "WebSocket działa na porcie 8765"
            )


            await asyncio.Future()



    asyncio.run(
        main()
    )



if __name__ == "__main__":


    Thread(
        target=websocket_thread,
        daemon=True
    ).start()



    app.run(

        host="0.0.0.0",

        port=5000,

        debug=False

    )