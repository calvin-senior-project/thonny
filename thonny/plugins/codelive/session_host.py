import json
import sys
from threading import Thread, Event, Lock
from queue import Queue
import time
import struct
import pickle

#import context  # Ensures paho is in PYTHONPATH
import paho.mqtt.client as mqtt

#from threading import Thread
#from queue import SimpleQueue

from thonny import get_workbench
from tkinter import PhotoImage

WORKBENCH = get_workbench()
QOS = 0
BROKER = 'test.mosquitto.org'
PORT = 1883
exitFlag = Event()
global workQueue
workQueue = Queue(30)

# Precursors for Host class methods
class Host(mqtt.Client):
    def __init__(self, thread_nums):
        super().__init__()
        print("*****")
        print("Initializing connection...")
        print("*****")
        self.threads = []
        self.connect(BROKER, PORT, 60)

        for threadID in range(thread_nums):
            self.threads.append(ProcessThread("Thread"+str(threadID), self))
    
    def run(self):
        for t in self.threads:
            t.start()
    
    def on_connect(self, client, userdata, rc, *extra_params):
        print('Connected with result code='+str(rc))
        self.subscribe("Calvin/CodeLive/Change", qos=QOS)

    def on_message(self, client, data, msg):
        if msg.topic == "Calvin/CodeLive/Change":
            if msg:
                if msg == "END":
                    print("end")
                else:
                    workQueue.put(msg.payload)

    #closes client and terminates threads
    def kill(self):
        print("closing")
        self.close()
        exitFlag.set()
        for t in self.threads:
            t.join()

###################################

class ProcessThread(Thread):
    def __init__(self, name, client):
        Thread.__init__(self)
        self._name = name
        self._editor_notebook = WORKBENCH.get_editor_notebook()
        self._end = False

    def receive(self, sock):
        chunk = sock.recv(MSGLEN)
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        return chunk

    def send_response(self, client, message):
        (result, num) = client.publish('Calvin/CodeLive/Change', message, qos=QOS)
        print("sent response:", message)
        if result != 0:
            print('PUBLISH returned error:', result)

    def makeChange(self, sock):
        while True:
            msg = workQueue.get()
            if msg:
                codeview = self._editor_notebook.get_current_editor().get_text_widget()
                print("command: %s\tposition: %s\tsrting: %s" % (msg[0], msg[2:msg.find("]")], msg[msg.find("]") + 1:]))
                if msg[0] == "I":
                    position = msg[2 : msg.find("]")]
                    new_text = msg[msg.find("]") + 1 : ]
                    codeview.insert(position, new_text)
                elif msg[0] == "D":
                    codeview.delete(msg[2:msg.find("]")])
                elif msg[0] == "R":
                    codeview.insert(position, '')
                    codeview.insert(position, '\r')
                elif msg[0] == "T":
                    codeview.insert(position, '\t')
                elif len(msg) >= 5 and msg[0 : 5] == "FIRST":
                    # self.insert_cursor(codeview, msg[6 : msg.find("]")])
                    pass
            else:
                print("...")
            if exitFlag.is_set():
                break
            time.sleep(.25)


if __name__ == "__main__":
    # Unit Tests
    pass
