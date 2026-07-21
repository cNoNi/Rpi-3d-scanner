from gpiozero import OutputDevice
from time import sleep



en = OutputDevice(4)
step = OutputDevice(17)
direction = OutputDevice(27)

en.off()

direction.on()



ms1 = OutputDevice(22)
ms2 = OutputDevice(23)
ms3 = OutputDevice(24)


microstepping = True

if microstepping:
    ms1.on()
    ms2.on()
    ms3.on()
else:
    ms1.off()
    ms2.off()
    ms3.off()


while True:
    step.on()
    sleep(0.01)
    step.off()
    sleep(0.01)
