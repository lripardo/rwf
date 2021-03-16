from gpiozero import DigitalOutputDevice, DigitalInputDevice
from time import sleep

pump = DigitalOutputDevice(17)
sensor1 = DigitalInputDevice(27)
sensor2 = DigitalInputDevice(22)

while True:
    print("Sensor 1 = {0}, Sensor 2 = {1}\n", sensor1.value, sensor2.value)
    sleep(10)
