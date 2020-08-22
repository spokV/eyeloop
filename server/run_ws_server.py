'''
The MIT License (MIT)
Copyright (c) 2013 Dave P.
'''

import signal
import sys
import ssl
import json
import settings
import helpers
import cv2
import uuid
#import redis
import time
import numpy as np
from threading import Thread
from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer, SimpleSSLWebSocketServer
from optparse import OptionParser
#from vidgear.stabilizer import Stabilizer
#import vidgear.helper

#db = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
clients = []
#stab = Stabilizer(smoothing_radius=5, logging=True)
stabilize = 0

def prepare_image_ad(image, target):
    # resize the input image and preprocess it
    nparr = helpers.base64_decode_buffer(image, np.uint8)
    #print(nparr.shape)
    image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    #print(image.shape)
    if stabilize == 1:
       stabilized_frame = stab.stabilize(image)
       if stabilized_frame is None:
          return None
       else:
          image = stabilized_frame
    image = image / 255

    frame_preprocessed = np.zeros((settings.IMAGE_HEIGHT, settings.IMAGE_WIDTH, 1), dtype=np.float16)
    frame_preprocessed[:, :, :] = image.reshape(settings.IMAGE_HEIGHT, settings.IMAGE_WIDTH, 1)
    return frame_preprocessed

#clients = []
#stab = Stabilizer(smoothing_radius=5, logging=True)
#stabilize = 1
class ProcessFrames(WebSocket):

   def handleMessage(self):
      if self.opcode == 1:
         frame = json.loads(self.data)
         image_idx = frame['image_idx']
         image = prepare_image_ad(frame['image'], (settings.IMAGE_HEIGHT, settings.IMAGE_WIDTH))
         if image is None:
            return
         image = image.copy(order="C")

         print("rcv img idx: ", image_idx) 
         # generate an ID for the classification then add the
         # classification ID + image to the queue
         #k = str(uuid.uuid4())
         #d = {"id": k, "image_idx": str(image_idx), "image": helpers.base64_encode_image(image)}
         #db.rpush(settings.IMAGE_QUEUE, json.dumps(d))
      #print('data: ', self.data)
      #self.sendMessage(self.data)

   def handleConnected(self):
      clients.append(self)
      db.flushdb()
      print('connect')
      pass

   def handleClose(self):
      clients.clear()
      db.flushdb()
      print('close')
      pass

#clients = []
#class SimpleChat(WebSocket):

#   def handleMessage(self):
#      for client in clients:
#         if client != self:
#            client.sendMessage(self.address[0] + u' - ' + self.data)

#   def handleConnected(self):
#      print (self.address, 'connected')
#      for client in clients:
#         client.sendMessage(self.address[0] + u' - connected')
#      clients.append(self)

#   def handleClose(self):
#      clients.remove(self)
#      print (self.address, 'closed')
#      for client in clients:
#         client.sendMessage(self.address[0] + u' - disconnected')

def prediction_feeder(name):
   max_output_return_itr = 0
   data = {}
   while True:
      output = db.lpop(settings.PREDICT_QUEUE)

      if output is not None:
         #if max_output_return_itr > settings.MIN_BATCH_SIZE:
         #   break
         #max_output_return_itr = max_output_return_itr + 1
         #print("pop")
         output = output.decode("utf-8")
         data["predictions"] = json.loads(output)
         # deserialize the object and obtain the input image
         #output = db.lpop(settings.PREDICT_QUEUE)
         data["success"] = True
         try:
            clients[0].sendMessage(json.dumps(data))#.encode('utf8'))
         except:
            print('')
      else:
         time.sleep(settings.CLIENT_SLEEP)
      #time.sleep(1)

if __name__ == "__main__":

   parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
   parser.add_option("--host", default='', type='string', action="store", dest="host", help="hostname (localhost)")
   parser.add_option("--port", default=8000, type='int', action="store", dest="port", help="port (8000)")
   parser.add_option("--example", default='echo', type='string', action="store", dest="example", help="echo, chat")
   parser.add_option("--ssl", default=0, type='int', action="store", dest="ssl", help="ssl (1: on, 0: off (default))")
   parser.add_option("--cert", default='./cert.pem', type='string', action="store", dest="cert", help="cert (./cert.pem)")
   parser.add_option("--key", default='./key.pem', type='string', action="store", dest="key", help="key (./key.pem)")
   parser.add_option("--ver", default=ssl.PROTOCOL_TLSv1, type=int, action="store", dest="ver", help="ssl version")
   parser.add_option("--stabilize", default=0, type='int', action="store", dest="stabilize", help="stabilize (1: on, 0: off (default))")

   (options, args) = parser.parse_args()

   #db.flushdb()
   cls = ProcessFrames
   stabilize = options.stabilize

   print(settings.ALS_LOG, "Server VERSION: ", settings.VERSION)
   if options.ssl == 1:
      server = SimpleSSLWebSocketServer(options.host, options.port, cls, options.cert, options.key, version=options.ver)
   else:
      server = SimpleWebSocketServer(options.host, options.port, cls)

   #t = Thread(target=prediction_feeder, args=(1,))
   #t.daemon = True
   #t.start()
   #print(settings.ALS_LOG, 'prediction feeder thread - start')

   def close_sig_handler(signal, frame):
      server.close()
      sys.exit()

   signal.signal(signal.SIGINT, close_sig_handler)

   server.serveforever()
