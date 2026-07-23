import os
import asyncio

from threading import Event


class Camera:

    def __init__(
        self,
        image_dir
    ):

        self.image_dir = image_dir

        os.makedirs(
            self.image_dir,
            exist_ok=True
        )

        self.phone = None
        self.loop = None

        self.photo_done = Event()



    def set_connection(
        self,
        websocket,
        loop
    ):

        self.phone = websocket
        self.loop = loop

        print(
            "Camera: telefon podłączony"
        )



    def disconnect(self):

        self.phone = None
        self.loop = None

        self.photo_done.clear()

        print(
            "Camera: telefon rozłączony"
        )



    async def _send_take_photo(self):

        if self.phone:

            await self.phone.send(
                "take_photo"
            )



    def take_photo(
        self,
        filename
    ):

        if self.phone is None:
            raise RuntimeError(
                "Telefon nie jest podłączony"
            )


        if self.loop is None:
            raise RuntimeError(
                "Brak websocket loop"
            )


        self.photo_done.clear()


        asyncio.run_coroutine_threadsafe(
            self._send_take_photo(),
            self.loop
        )


        success = self.photo_done.wait(
            timeout=10
        )


        if not success:
            raise TimeoutError(
                "Telefon nie potwierdził zdjęcia"
            )


        filepath = os.path.join(
            self.image_dir,
            filename
        )


        print(
            f"Zdjęcie wykonane: {filepath}"
        )


        return filepath



    def photo_taken(self):

        self.photo_done.set()