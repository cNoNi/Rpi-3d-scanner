import os
import asyncio

from threading import Event


class Camera:

    def __init__(self,image_dir):
        self.image_dir = image_dir

        os.makedirs(
            self.image_dir,
            exist_ok=True
        )

        self.phone = None
        self.loop = None

        self.photo_done = Event()

    def set_connection(self,websocket,loop):
        self.phone = websocket
        self.loop = loop

        print("Camera: telefon podłączony")

    def disconnect(self, websocket):
        # rozłącz tylko, jeśli to aktualne połączenie
        if self.phone is websocket:
            self.phone = None
            self.loop = None
            self.photo_done.clear()
            print("Camera: telefon rozłączony")


    async def _send_take_photo(self):
        if self.phone:
            await self.phone.send(
                "take_photo"
            )



    def take_photo(self, filename):
        phone, loop = self.phone, self.loop

        if phone is None or loop is None:
            raise RuntimeError("Telefon nie jest podłączony")

        self.photo_done.clear()

        future = asyncio.run_coroutine_threadsafe(
            phone.send("take_photo"),
            loop,
        )
        future.result(timeout=5)  # rzuci wyjątek, jeśli wysyłka się nie udała

        if not self.photo_done.wait(timeout=10):
            raise TimeoutError("Telefon nie potwierdził zdjęcia")

        return os.path.join(self.image_dir, filename)



    def photo_taken(self):

        self.photo_done.set()