import socket
import threading
import time

import cv2
import numpy as np


class CmdThread(threading.Thread):
    def __init__(self, app):
        self.app = app
        self._running = True
        self.data = b""

        HOST = ''
        PORT = 8485

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Socket created')

        self.s.bind((HOST, PORT))
        print('Socket bind complete')

        threading.Thread.__init__(self)

    def run(self):
        print("Start CMD Thread")
        self.s.listen(10)
        print('Socket now listening')

        conn, addr = self.s.accept()
        while self._running:
            print("here")
            self.data += conn.recv(4096)
            time.sleep(1)


class ClosedLoop_shai_Extractor:
    def __init__(self, MAXSIZE=3231):
        """
        RUN CALIBRATE, THEN SET MAXSIZE (= ._cal_ file value)
        """

        self.basesize = MAXSIZE / 2
        self.start_threads()

    def start_threads(self):
        self.cmd_thread = CmdThread(self)
        self.cmd_thread.deamon = True
        self.cmd_thread.start()

    def activate(self) -> None:
        self.start = time.time()
        self.step_start = time.time()
        self.current = self.start

        # self.fetch = self.r_fetch

    def timer(self):
        return time.time() - self.step_start

    def release(self):
        return

    def fetch(self, engine):
        w, h = engine.dataout["pupil"][0]
