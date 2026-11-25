from contextlib import contextmanager


class FakeMotor:
    def __init__(self, position=0):
        self.position = position
        self.visited = []
        self.enabled_now = False

    @contextmanager
    def enabled(self):
        self.enabled_now = True
        try:
            yield self
        finally:
            self.enabled_now = False

    def move_to(self, target, should_stop=None):
        if should_stop is not None and should_stop():
            return False
        self.position = target
        self.visited.append(target)
        return True

    def move_by(self, delta, should_stop=None):
        return self.move_to(self.position + delta, should_stop)


class FakeCamera:
    def __init__(self, fail_on=None):
        self.connected = True
        self.photos = []
        self.fail_on = fail_on
        self.gate = None  # optional Event that blocks every photo until set

    def take_photo(self, name="photo"):
        if self.gate is not None:
            self.gate.wait(5)
        if self.fail_on is not None and len(self.photos) == self.fail_on:
            raise RuntimeError("camera exploded")
        self.photos.append(name)
