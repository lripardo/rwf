import datetime

from gpiozero import DigitalOutputDevice, DigitalInputDevice
from time import sleep
from firebase_admin import firestore

import firebase_admin

pump = DigitalOutputDevice(17)  # GPIO 17
sensor1 = DigitalInputDevice(27)  # GPIO 27
sensor2 = DigitalInputDevice(22)  # GPIO 22

verification_delay_pump_on = 10  # 10 seconds
verification_delay_pump_off = 600  # 10 minutes
max_pump_on_time = 600  # 10 minutes
sleep_pump_time = 600  # 10 minutes
verification_delay = verification_delay_pump_off  # default pump off
last_pump_on_time = None
last_pump_off_time = None

# Point your GOOGLE_APPLICATION_CREDENTIALS env var to credentials json file
firebase_admin.initialize_app()
db = firestore.client()


def register_event(value):
    try:
        now = datetime.datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        time = now.strftime("%H_%M_%S")
        doc_ref = db.collection(year).document(month).collection(day).document(time)
        doc_ref.set({
            u'timestamp': firestore.SERVER_TIMESTAMP,
            u'pump': value
        })
    except Exception as e:
        print(e)


while True:
    print("Sensor(1)={0}, Sensor(2)={1}, Delay={2}\n".format(sensor1.value, sensor2.value, verification_delay))

    # Avoid lock on pump
    if last_pump_on_time and verification_delay == verification_delay_pump_on:
        seconds = int((datetime.datetime.now() - last_pump_on_time).total_seconds())
        if seconds > max_pump_on_time:
            print("Pump locked...")
            verification_delay = verification_delay_pump_off
            pump.off()
            break  # Exit application

    if not sensor1.value and not sensor2.value and verification_delay == verification_delay_pump_off:
        verification_delay = verification_delay_pump_on
        pump.on()
        last_pump_on_time = datetime.datetime.now()
        register_event(1)
    elif sensor1.value and sensor2.value and verification_delay == verification_delay_pump_on:
        # Obey the delay sleep pump
        if last_pump_off_time:
            seconds = int((datetime.datetime.now() - last_pump_off_time).total_seconds())
            if seconds <= sleep_pump_time:
                print("Pump sleeping...")
                break  # Exit application
        verification_delay = verification_delay_pump_off
        pump.off()
        last_pump_off_time = datetime.datetime.now()
        register_event(0)
    sleep(verification_delay)
