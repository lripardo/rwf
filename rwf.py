import os
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from time import sleep

import firebase_admin
from firebase_admin import firestore
from gpiozero import DigitalOutputDevice, DigitalInputDevice
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

VERIFICATION_DELAY_PUMP_ON = 10  # 10 seconds
VERIFICATION_DELAY_PUMP_OFF = 600  # 10 minutes
MAX_PUMP_ON_TIME = 480  # 8 minutes
SLEEP_PUMP_TIME = 600  # 10 minutes

rfw = None


def alert_email(message):
    email = os.environ.get("RWF_EMAIL")
    api_key = os.environ.get("SENDGRID_API_KEY")
    if email and api_key:
        message = Mail(
            from_email=email,
            to_emails=email,
            subject="RWF Alert",
            html_content="<strong>{0}</strong>".format(message))
        try:
            sg = SendGridAPIClient()
            response = sg.send(message)
            print("Email alert sent with status code: {0}".format(response.status_code))
        except Exception as e:
            print("Email alert error: {0}".format(e))


def print_constraint(constraint, message):
    m = "{0} constraint => {1}. Server will be shutdown...".format(constraint, message)
    print(m)
    return m


def set_firebase(value):
    try:
        now = datetime.now()
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


class RWFHttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        response = '{{"status": {0}, "message": "{1}", "data": {2}}}'
        status = 400
        message = "error"
        data = "null"

        if rwf:
            rwf.read()
            status = 200
            message = "Ok"
            d = '{{"sensor1": {0}, "sensor2": {1}, "delay": {2}}}'
            data = d.format(rwf.sensor1(), rwf.sensor2(), rwf.verification_delay())

        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        data = response.format(status, message, data)
        self.wfile.write(bytes(data, "utf8"))


class RWF:
    def __init__(self):
        self._value1 = 0
        self._value2 = 0
        self._pump = DigitalOutputDevice(17)  # GPIO 17
        self._sensor1 = DigitalInputDevice(27)  # GPIO 27
        self._sensor2 = DigitalInputDevice(22)  # GPIO 22
        self._verification_delay = VERIFICATION_DELAY_PUMP_OFF  # default pump off
        self._last_pump_on_time = None
        self._last_pump_off_time = None

    def pump_off(self):
        self._pump.off()
        self._verification_delay = VERIFICATION_DELAY_PUMP_OFF
        self._last_pump_off_time = datetime.now()
        set_firebase(0)

    def pump_on(self):
        self._pump.on()
        self._verification_delay = VERIFICATION_DELAY_PUMP_ON
        self._last_pump_on_time = datetime.now()
        set_firebase(1)

    def print(self):
        message = "Sensor(1)={0}, Sensor(2)={1}, Delay={2}\n"
        print(message.format(self._value1, self._value2, self._verification_delay))

    def read(self):
        self._value1 = self._sensor1.value
        self._value2 = self._sensor2.value

    def is_pump_on(self):
        return self._verification_delay == VERIFICATION_DELAY_PUMP_ON

    def sensor1(self):
        return self._value1

    def sensor2(self):
        return self._value2

    def elapsed_seconds_last_pump_off(self):
        if self._last_pump_off_time:
            return (datetime.now() - self._last_pump_off_time).total_seconds()
        return 0

    def elapsed_seconds_last_pump_on(self):
        if self._last_pump_on_time:
            return (datetime.now() - self._last_pump_on_time).total_seconds()
        return 0

    def sleep(self):
        sleep(self._verification_delay)

    def verification_delay(self):
        return self._verification_delay


if __name__ == "__main__":
    alert_email("Server started...")
    server = HTTPServer(("0.0.0.0", 8000), RWFHttpHandler)
    threading.Thread(target=server.serve_forever).start()

    rwf = RWF()

    # Point your GOOGLE_APPLICATION_CREDENTIALS env var to credentials json file
    firebase_admin.initialize_app()
    db = firestore.client()

    while True:
        rwf.read()
        rwf.print()

        # Avoid pump on lock
        elapsed_seconds_last_pump_on = rwf.elapsed_seconds_last_pump_on()
        if elapsed_seconds_last_pump_on and rwf.is_pump_on() and elapsed_seconds_last_pump_on > MAX_PUMP_ON_TIME:
            alert_email(print_constraint("Pump", "Locked"))
            rwf.pump_off()
            quit(1)  # Exit application

        if not rwf.sensor1() and not rwf.sensor2() and not rwf.is_pump_on():
            # Obey the delay sleep pump
            elapsed_seconds_last_pump_off = rwf.elapsed_seconds_last_pump_off()
            if elapsed_seconds_last_pump_off and elapsed_seconds_last_pump_off <= SLEEP_PUMP_TIME:
                alert_email(print_constraint("Pump", "Delay sleep"))
                quit(1)  # Exit application
            rwf.pump_on()
        elif rwf.sensor1() and rwf.sensor2() and rwf.is_pump_on():
            rwf.pump_off()
        elif not rwf.sensor1() and rwf.sensor2():
            alert_email(print_constraint("Sensor", "Sensor 1 == 0 and Sensor 2 == 1"))
            quit(1)  # Exit application

        rwf.sleep()
