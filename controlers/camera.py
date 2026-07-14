import subprocess
from pathlib import Path
from datetime import datetime


class CameraError(Exception):
    """Wyjątek zgłaszany przy błędach aparatu."""
    pass


class Camera:

    def __init__(self, image_dir="photos"):
        self.image_dir = Path(image_dir)
        self.image_dir.mkdir(parents=True, exist_ok=True)
        self.clear_images(image_dir)

    def detect(self):
        """Sprawdza, czy aparat jest podłączony."""
        result = subprocess.run(
            ["gphoto2", "--auto-detect"],
            capture_output=True,
            text=True
        )

        return "usb:" in result.stdout.lower()

    def take_photo(self, filename=None):
        """
        Robi zdjęcie i zapisuje je na dysku.

        Zwraca:
            Path do zapisanego pliku.
        """

        if filename is None:
            filename = datetime.now().strftime("%Y%m%d_%H%M%S.jpg")

        filepath = self.image_dir / filename

        command = [
            "gphoto2",
            "--capture-image-and-download",
            "--force-overwrite",
            "--filename",
            str(filepath)
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise CameraError(result.stderr.strip())

        return filepath

    def summary(self):
        """Zwraca informacje o aparacie."""

        result = subprocess.run(
            ["gphoto2", "--summary"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise CameraError(result.stderr.strip())

        return result.stdout
    

    def clear_images(folder):
        folder = Path(folder)

        for file in folder.glob("*.jpg"):
            file.unlink()