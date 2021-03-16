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

while True:
    if not sensor1.value and not sensor2.value and verification_delay == verification_delay_pump_off:
        verification_delay = verification_delay_pump_on
        pump.on()
        doc_ref = db.collection(u'events').document()
        doc_ref.set({
            u'timestamp': firestore.SERVER_TIMESTAMP,
            u'pump': 1
        })
    elif sensor1.value and sensor2.value and verification_delay == verification_delay_pump_on:
        verification_delay = verification_delay_pump_off
        pump.off()
        doc_ref = db.collection(u'events').document()
        doc_ref.set({
            u'timestamp': firestore.SERVER_TIMESTAMP,
            u'pump': 0
        })
    sleep(verification_delay)
