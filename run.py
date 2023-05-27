#!/usr/bin/env python3
import logging
from utils.Sensor import Sensor
from utils.Cam import Cam
from utils.JWTClient import JWTClient
import time


def setup_log():
    log_formatter = logging.Formatter("%(asctime)-15s %(levelname)-8s %(message)s")
    root_logger = logging.getLogger()

    file_handler = logging.FileHandler("log.txt", mode="a+", encoding="utf-8")
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)


def main():
    setup_log()

    logging.info("Hello, World!")
    cam = Cam()
    sensor = Sensor()
    client = JWTClient()
    client_device = client.get("/device/get")
    device_id = int(client_device.get('data').get('id'))

    logging.info("Hello, Your device id is %s", device_id)

    while True:
        try:
            sensor_data = sensor.read_all()
            image_b64 = cam.capture_img()
            logging.info("Got sensor data: %s", sensor_data)
            req = {
                'deviceId': device_id,
                'temperature': sensor_data[0][0],
                'relativeHumidity': sensor_data[0][1],
                'soilHumidity': sensor_data[1][6],
                'imageBase64': image_b64
            }
            client.post('log/write', req)
        except Exception as e:
            logging.error("Unhandled Exception while running loop: %s", e)
        time.sleep(60)


if __name__ == '__main__':
    main()
