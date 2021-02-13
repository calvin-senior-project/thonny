import paho.mqtt.client as mqtt
import time
import string
import random
import os

from thonny import get_workbench

WORKBENCH = get_workbench()

BROKER_URLS = [
    "test.mosquitto.org",
    "mqtt.eclipse.org",
    "broker.hivemq.com",
    "mqtt.fluux.io",
    "broker.emqx.io"
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

def test_broker(url):
    client = mqtt.Client()
    try:
        #it seems as if keepalive only takes integers
        client.connect(url, 1883, 1)
        return True
    except Exception: 
        return False 
    
def get_default_broker():
    global BROKER_URLS

    for broker in BROKER_URLS:
        if test_broker(broker):
            return broker

    return None

def assign_broker(broker_url = None):
    if test_broker(broker_url):
        return broker_url
    else:
        return get_default_broker()

class MqttConnection(mqtt.Client):
    def __init__(self, 
                 session,
                 broker_url, 
                 port = None, 
                 qos = 0, 
                 delay = 1.0, 
                 topic = None,
                 on_message = None,
                 on_publish = None,
                 on_connect = None):
        mqtt.Client.__init__(self)
        self.session = session
        self.broker = assign_broker(broker_url) #TODO: Handle assign_broker returning none
        self.port = port or self.get_port()
        self.qos = qos
        self.delay = delay
        #TODO: Intergrate get_topic, @Sam not sure what you wanted to do with the name param
        #    program currently fails if not supplied a topic
        self.topic = topic 
        
        if topic == None:
            print("New Topic: %s" % self.topic)
        else:
            print("Existing topic: %s" % self.topic)

    @classmethod
    def handshake(cls, name, topic, broker):
        
        '''
        x = mqtt.CLient()
        x.connect(...)

        - publish message saying im a new user
        - block till you get a reply
        - when u get a reply, parse into a dict with keys id, name, docs (list), users (list)
        - return these
        '''
        editors = list(WORKBENCH.get_editor_notebook().winfo_children())
        
        dummy_val = {"id": 1,
                     "name" : name,
                     "broker" : broker,
                     "is_cohost" : True,
                     "editors" : editors
                     }
        return dummy_val

    def get_port(self):
        return 1883
    
    def get_topic(self, name):
        return name# + "_" + ''.join(random.choice(string.ascii_uppercase) for i in range(6))

    # Callback when connecting to the MQTT broker
    # def on_connect(self, userdata, flags, rc):
    #     if rc==0:
    #         print('Connected to ' + self.broker)

    def on_message(self, client, data, msg):
        instr = msg.payload.decode("utf-8")

        if get_sender_id(instr) == self.session.user_id:
            return

        if msg.topic == self.topic:
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

    myConnection = MqttConnection(x, assign_broker(), topic = generate_topic())
    myConnection.Connect()
    myConnection.loop_start()

    while True:
        x = input("Type")
        try:
            myConnection.publish("testing ")
        except KeyboardInterrupt:
            print("Done")
            myConnection.disconnect()
