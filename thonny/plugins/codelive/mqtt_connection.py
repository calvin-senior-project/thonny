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

# Callback when a message is published
def publish_callback(client, userdata, mid):
    print("sent")
    #do something

# Callback when connecting to the MQTT broker
def connect_callback(client, userdata, flags, rc):
    if rc==0:
        print('Connected to ' + client.broker)
        #do something

# Callback when client receives a PUBLISH message from the broker
def message_callback(client, data, msg):
    if msg.topic == client.topic:
        print(msg.payload.decode("utf-8"))
        WORKBENCH.event_generate("RemoteChange", change=msg.payload.decode("utf-8"))

class MqttConnection(mqtt.Client):
    def __init__(self, 
                 session_name, 
                 broker_url = None, 
                 port = None, 
                 qos = 0, 
                 delay = 1.0, 
                 topic = None,
                 on_message = None,
                 on_publish = None,
                 on_connect = None):
        mqtt.Client.__init__(self)
        self.broker = broker_url or self.get_default_broker()
        self.port = port or self.get_port()
        self.qos = qos
        self.delay = delay
        self.topic = topic or self.get_topic(session_name)
        
        if topic == None:
            print("New Topic: %s" % self.topic)
        else:
            print("Existing topic: %s" % self.topic)

        self.on_connect = on_connect or connect_callback
        self.on_message = on_message or message_callback
        self.on_publish = on_publish or publish_callback
    
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
    
    def on_publish(self, userdata, mid):
        print("sent")
        #do something

    # Callback when connecting to the MQTT broker
    def on_connect(self, userdata, flags, rc):
        if rc==0:
            print('Connected to ' + self.broker)

    def on_message(self, client, data, msg):
        if msg.topic == self.topic:
            print(msg.payload.decode("utf-8"))
            WORKBENCH.event_generate("RemoteChange", change=msg.payload.decode("utf-8"))
    
    def publish(self, msg):
        mqtt.Client.publish(self, self.topic, msg)

    def Connect(self):
        mqtt.Client.connect(self, self.broker, self.port, 60)
        mqtt.Client.subscribe(self, self.topic, qos=self.qos)

if __name__ == "__main__":
    myConnection = MqttConnection("John_Doe")
    myConnection.connect()
    myConnection.loop_start()

    try:
        myConnection.publish("testing ")
    except KeyboardInterrupt:
        print("Done")
        myConnection.disconnect()
