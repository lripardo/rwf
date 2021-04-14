from gpiozero import DigitalOutputDevice, DigitalInputDevice
from time import sleep
import firebase_admin
from firebase_admin import firestore

pump = DigitalOutputDevice(17)  # GPIO 17
sensor1 = DigitalInputDevice(27)  # GPIO 27
sensor2 = DigitalInputDevice(22)  # GPIO 22

verification_delay_pump_on = 10  # 10 seconds
verification_delay_pump_off = 600  # 10 minutes
verification_delay = verification_delay_pump_off  # default pump off

# Point your GOOGLE_APPLICATION_CREDENTIALS env var to credentials json file
firebase_admin.initialize_app()
db = firestore.client()
events_collection = u'events'


def register_event(value):
    try:
        doc_ref = db.collection(events_collection).document()
        doc_ref.set({
            u'timestamp': firestore.SERVER_TIMESTAMP,
            u'pump': value
        })
    except Exception as e:
        print(e)


while True:
    print("Sensor(1)={0}, Sensor(2)={1}, Delay={2}\n".format(sensor1.value, sensor2.value, verification_delay))
    if not sensor1.value and not sensor2.value and verification_delay == verification_delay_pump_off:
        verification_delay = verification_delay_pump_on
        pump.on()
        register_event(1)
    elif sensor1.value and sensor2.value and verification_delay == verification_delay_pump_on:
        verification_delay = verification_delay_pump_off
        pump.off()
        register_event(0)
    sleep(verification_delay)
