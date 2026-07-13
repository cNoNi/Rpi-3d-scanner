from camera import Camera

camera = Camera("photos")

if camera.detect():
    print("Aparat znaleziony.")

    photo = camera.take_photo()

    print(f"Zdjęcie zapisane jako {photo}")

else:
    print("Nie znaleziono aparatu.")