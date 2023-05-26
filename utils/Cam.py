#!/usr/bin/env python3
import base64

import cv2
import time
import logging
from time import time
from threading import Thread


class Cam:
    cam = None
    current = time()
    previous = time()
    delta = 0
    thread = None
    last_out = None

    def __init__(
        self,
        device_id=0,
        interval=60,
        width=1920,
        height=1080,
        save_loc="/home/pi/monsys/output/",
    ):
        self.device_id = device_id
        self.interval = interval
        self.width = width
        self.height = height
        self.save_loc = save_loc

    def open(self):
        try:
            if self.check_open():
                print("Already opened")
                return
            self.cam = cv2.VideoCapture(self.device_id, cv2.CAP_V4L2)
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        except Exception as e:
            print(e)
            self.release()

    def check_open(self):
        return self.cam is not None and self.cam.isOpened()

    def release(self):
        print("Releasing cam...")
        if self.cam is not None:
            self.cam.release()

    def capture_img(self):
        if not self.check_open():
            self.open()

        try:
            ret, img = self.cam.read()
            if not ret:
                logging.error("Image not captured")
                return
            ret, buff = cv2.imencode('.jpg', img);
            if not ret:
                logging.error("Image not encoded")
                return
            b64 = base64.b64encode(buff)
            b64 = "data:image/jpeg;base64," + b64
            return b64

        except Exception as e:
            logging.error("Unhandled exception:", e)

        # saving memory
        self.release()