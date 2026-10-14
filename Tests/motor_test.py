from gpiozero import OutputDevice
from time import sleep

# Numery pinów GPIO (BCM)
STEP_PIN = 16    # przykładowo GPIO27
DIR_PIN = 20     # przykładowo GPIO22
EN_PIN = 26

step = OutputDevice(STEP_PIN)
direction = OutputDevice(DIR_PIN)
en = OutputDevice(EN_PIN)
# Kierunek obrotu
direction.on()


en.off()
# 400 kroków/s
steps_per_second = 400
delay = 1 / (steps_per_second * 2)

while True:
    step.on()
    sleep(delay)
    step.off()
    sleep(delay)
