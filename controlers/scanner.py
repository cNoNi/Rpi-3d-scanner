from time import sleep


class Scanner:

    def __init__(
        self,
        motor,
        camera,
        photos_per_revolution=100,
        pre_wait=2,
        post_wait=2,
        on_status_change=None,
	steps_per_revolution=200
    ):

        self.motor = motor
        self.camera = camera

        self.photos_per_revolution = photos_per_revolution
	self.steps_per_revolution = steps_per_revolution

        self.pre_wait = pre_wait
        self.post_wait = post_wait

        self.running = False
        self.current_photo = 0

        self.on_status_change = on_status_change


    def notify(self):
        if self.on_status_change:
            self.on_status_change(self.status())

    def motor_setup(self):
	self.motor.set_motor_enabled(True)
	self.motor.run_to_position_steps(0)
	self.motor.set_microstepping_resolution(1)


    def start(self):

        if self.running:
        	return

	motor_setup()

        self.running = True
        self.current_photo = 0
        self.notify()

	'''
        total_steps = (
            self.motor.steps_per_revolution //
            self.photos_per_revolution
        )
	'''
	step_per_photo = (
		self.steps_per_revolution /
		self.photos_per_revolution
	)
	'''
        try:

            while (
                self.running and
                self.current_photo < self.photos_per_revolution
            ):

                self.motor.rotate_steps(
                    total_steps,
                    clockwise=True
                )

                sleep(self.pre_wait)

                filename = f"image_{self.current_photo:04d}.jpg"
                self.camera.take_photo(filename)

                sleep(self.post_wait)

                self.current_photo += 1
                self.notify()

        finally:
            self.running = False
            self.notify()
	'''
	try:
        	for photo in range(self.photos_per_revolution):

	            	if not self.running:
        	        	break

            		filename = f"image_{photo:04d}.jpg"

            		sleep(self.pre_wait)
            		self.camera.take_photo(filename)
            		sleep(self.post_wait)

            		self.current_photo = photo + 1
            		self.notify()

            		if photo == self.photos_per_revolution - 1:
                		break

            		target = round((photo + 1) * step_per_photo)
			self.motor.run_to_position_steps(target)

    	finally:
       		self.running = False
       		self.notify()

	def stop(self):
		self.motor.set_motor_enabled(False)
        	self.running = False
        	self.notify()


    	def status(self):

        	return {
            		"running": self.running,
            		"photo": self.current_photo,
            		"total": self.photos_per_revolution
        	}
