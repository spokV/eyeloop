import socket
import sys
import cv2
import pickle
import numpy as np
import struct ## new
import zlib

HOST=''
PORT=8485

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print('Socket created')

s.bind((HOST,PORT))
print('Socket bind complete')
s.listen(10)
print('Socket now listening')

conn,addr=s.accept()
#conn.settimeout(0.5)
cursor = (0, 0)
data = b""
payload_size = struct.calcsize(">LI")
print("payload_size: {}".format(payload_size))
need_to_bind_callbacks = True

def mousecallback(event, x, y, flags, params) -> None:
    global cursor
    #x = x % self.width
    cursor = (x, y)
    #print(cursor)

def remove_mousecallback() -> None:
    cv2.setMouseCallback("0", lambda *args: None)
    #cv2.setMouseCallback("4", lambda *args: None)

def add_mousecallback():
    try:
        cv2.setMouseCallback("0", mousecallback)
        #cv2.setMouseCallback("4", self.tip_mousecallback)
        print('add mouse callbacks')
    except Exception as inst:
        print(ins)
        print("Could not bind mouse-buttons.")

while True:
    while len(data) < payload_size:
        #print("Recv: {}".format(len(data)))
        data += conn.recv(4096)

    #print("Done Recv: {}".format(len(data)))
    #packed_msg_size = data[:payload_size]
    meta = data[:payload_size]
    data = data[payload_size:]
    imshow_context = 0
    #msg_size = struct.unpack(">L", packed_msg_size)[0]
    msg_size, imshow_context = struct.unpack(">LI", meta)

    #print("msg_size: {}".format(msg_size))
    while len(data) < msg_size:
        data += conn.recv(4096)
    frame_data = data[:msg_size]
    data = data[msg_size:]

    frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    #cv2.imshow('ImageWindow',frame)
    cv2.imshow(str(imshow_context), frame)
    if imshow_context == 0 and need_to_bind_callbacks == True:
        need_to_bind_callbacks = False
        add_mousecallback()
    
    #if cv2.waitKey(1) & 0xFF == ord('q'):
    key = (cv2.waitKey(1) & 0xFF)
    if key == ord('q'):
        break
    if key != 255:
        print(cursor)
        conn.sendall(struct.pack(">iii", key, cursor[0], cursor[1]))

remove_mousecallback()
