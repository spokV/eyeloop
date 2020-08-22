import socket
import sys
import cv2
import pickle
import numpy as np
import struct ## new
import zlib
from threading import Thread
import time
from multiprocessing import Process, Queue

HOST=''
PORT=8485

cursor = (0, 0)

class CommThread():
    def __init__(self):
        self.data = b""
        self.payload_size = struct.calcsize(">LI")
        print("payload_size: {}".format(self.payload_size))
        self._running = True
        
    def terminate(self):
        print('thread terminated')
        self._running = False

    def run(self, conn, outqueue):
        global key_pressed
        print('thread run')
        while self._running:
            while len(self.data) < self.payload_size:
                #print("Recv: {}".format(len(data)))
                self.data += conn.recv(4096)

            #print("Done Recv: {}".format(len(self.data)))
            meta = self.data[:self.payload_size]
            self.data = self.data[self.payload_size:]
            imshow_context = 0
            msg_size, imshow_context = struct.unpack(">LI", meta)

            #print("msg_size: {}".format(msg_size))
            while len(self.data) < msg_size:
                self.data += conn.recv(4096)
            frame_data = self.data[:msg_size]
            #print(len(self.data))
            self.data = self.data[msg_size:]
            
            frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
            #frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            
            outqueue.put((imshow_context, frame))

        conn.close()

def mousecallback(event, x, y, flags, params) -> None:
    global cursor
    cursor = (x, y)

def remove_mousecallback() -> None:
    cv2.setMouseCallback("0", lambda *args: None)
    #cv2.setMouseCallback("4", lambda *args: None)

def add_mousecallback():
    try:
        cv2.setMouseCallback("0", mousecallback)
        print('add mouse callbacks')
    except Exception as inst:
        print(inst)
        print("Could not bind mouse-buttons.")

if __name__ == '__main__':
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    print('Socket created')

    s.bind((HOST,PORT))
    print('Socket bind complete')
    outqueue = Queue(10)
    key_pressed = 255
    need_to_bind_callbacks = True

    while True:
        threads = []
        key_pressed = 255
        s.listen(10)
        print('Socket now listening')

        (conn,(ip,port)) = s.accept()
        need_to_bind_callbacks = True
        newThread = CommThread()
        t = Thread(target = newThread.run, args = (conn, outqueue, ), daemon = True)
        #newThread.setName('comm_thread')
        t.start()
        #print('New Thread')
        threads.append((newThread, t))
        
        while True:
            key_pressed = (cv2.waitKey(10) & 0xFF)
            if key_pressed == ord('q'):
                print('q')
                break
            if key_pressed != 255:
                print(cursor)
                conn.sendall(struct.pack(">iii", key_pressed, cursor[0], cursor[1]))
                key_pressed = 255
            
            context, frame = outqueue.get()
            if frame.size == 0:
                continue
            else:
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
                cv2.imshow(str(context), frame)
                if context == 0 and need_to_bind_callbacks == True:
                    need_to_bind_callbacks = False
                    add_mousecallback()
  
        print('t end')
        remove_mousecallback()
        cv2.destroyAllWindows()
        for t in threads:
            t[0].terminate()
            t[1].join()
    s.close()

