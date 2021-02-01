import paho.mqtt.client as mqtt
import time
import string
import random
import os

from thonny import get_workbench

WORKBENCH = get_workbench()

BROKER_URLS = [
    "test.mosquitto.org"
]

USER_COLORS = [
    "blue", 
    "green", 
    "red", 
    "pink", 
    "orange",
    "black",
    "white",
    "purple"
]

def topic_exists(s):
    # TODO: complete
    return False

def generate_topic():
    # TODO: complete
    existing_names = set()

    while True:
        name = "_".join([USER_COLORS[random.randint(0, len(USER_COLORS) - 1)] for _ in range(4)])
        name += ":" + "".join([str(random.randint(0, 9)) for _ in range(4)])

        if name in existing_names:
            continue

        if topic_exists(name):
            print("Topic %s is taken. Trying another random name..." % repr(name))
            existing_names.add(name)
        else:
            return name

def get_sender_id(instr):
    # TODO: Update to work with json
    return int(instr[instr.find("(") + 1 : instr.find("|")])

class MqttConnection(mqtt.Client):
    def __init__(self, 
                 session,
                 broker_url = None, 
                 port = None, 
                 qos = 0, 
                 delay = 1.0, 
                 topic = None,
                 on_message = None,
                 on_publish = None,
                 on_connect = None):
        mqtt.Client.__init__(self)
        self.session = session
        self.broker = broker_url or self.get_default_broker()
        self.port = port or self.get_port()
        self.qos = qos
        self.delay = delay
        self.topic = topic
        
        if topic == None:
            print("New Topic: %s" % self.topic)
        else:
            print("Existing topic: %s" % self.topic)

    def get_port(self):
        return 1883
    
    def get_topic(self, name):
        return name# + "_" + ''.join(random.choice(string.ascii_uppercase) for i in range(6))

    def get_default_broker(self):
        global BROKER_URLS

        for broker in BROKER_URLS:
            if self.test_broker(broker):
                return broker

        return None

    def test_broker(self, url):
        # TODO: add broker test
        return True

    # Callback when connecting to the MQTT broker
    # def on_connect(self, userdata, flags, rc):
    #     if rc==0:
    #         print('Connected to ' + self.broker)

    def on_message(self, client, data, msg):
        instr = msg.payload.decode("utf-8")

        if get_sender_id(instr) == self.session.user_id:
            print("instr ignored")
            return

        if msg.topic == self.topic:
            print(instr)
            WORKBENCH.event_generate("RemoteChange", change=instr)
    
    def publish(self, msg):
        mqtt.Client.publish(self, self.topic, msg)

    def Connect(self):
        mqtt.Client.connect(self, self.broker, self.port, 60)
        mqtt.Client.subscribe(self, self.topic, qos=self.qos)
    
    def get_sender(self, msg):
        pass

if __name__ == "__main__":
    import sys

    class Session_temp:
        def __init__(self, name = "John Doe", _id = 0):
            self.username = name
            self.user_id = _id
    
    x = Session_temp() if len(sys.argv) > 1 else Session_temp(_id = int(sys.argv[1]))
    myConnection = MqttConnection(x)
    myConnection.Connect()
    myConnection.loop_start()

    while True:
        x = input("Type")
        try:
            myConnection.publish("testing ")
        except KeyboardInterrupt:
            print("Done")
            myConnection.disconnect()
