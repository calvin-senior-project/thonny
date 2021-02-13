import paho.mqtt.client as mqtt
import time
import string
import random
import os
import json
import uuid
import sys
import thonny.plugins.codelive.utils as utils
import thonny.plugins.codelive.client as thonny_client
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

def get_sender_id(json_msg):
    return json_msg['id']

def get_instr(json_msg):
    return json_msg['instr']

def get_unique_code(json_msg):
    return json_msg['unique_code']

def get_id_assigned(json_msg):
    return json_msg['id_assigned']

def need_id(my_id):
    min_valid_id = 0
    if isinstance(my_id, int) and my_id < min_valid_id:
        return True
    return False

def test_broker(url):
    client = mqtt.Client()
    try:
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
        self.session = session #can access current ID of client
        self.broker = assign_broker(broker_url) #TODO: Handle assign_broker returning none
        self.port = port or self.get_port()
        self.qos = qos
        self.delay = delay
        self.topic = topic
        self.assigned_ids = [] #for handshake
        
        
        if topic == None:
            self.topic = generate_topic()
            print("New Topic: %s" % self.topic)
        else:
            print("Existing topic: %s" % self.topic)

    @classmethod
    def handshake(cls, name, topic, broker):
        #TODO: Minor bug where the cls stays "alive"
        temp_session = thonny_client.Session.create_session(name, topic, broker)
        temp_session.is_host = False
        temp_session.user_id = random.randint(-1000,-1)
        my_connection = cls(temp_session, broker, topic = topic)
        my_connection.Connect()
        my_connection.loop_start()

        my_code = str(uuid.uuid1())
        my_connection.publish(unique_code = my_code)

        while True:
            if my_connection.assigned_ids:
                sent_id, sent_code = my_connection.assigned_ids.pop()
                if sent_code == my_code:
                    break
        my_connection.loop_stop()
        editors = list(WORKBENCH.get_editor_notebook().winfo_children())
        
        return {"id": sent_id,
                "name": name,
                "broker": broker,
                "is_cohost": True, #TODO: Not sure how cohosts are assigned
                "editors" : editors
                }

    def get_port(self):
        return 1883
    
    # Callback when connecting to the MQTT broker
    # def on_connect(self, userdata, flags, rc):
    #     if rc==0:
    #         print('Connected to ' + self.broker)

    def on_message(self, client, data, msg):
        json_msg = json.loads(msg.payload)

        sender_id = get_sender_id(json_msg)
        if sender_id == self.session.user_id:
            print("instr ignored")
            return

        unique_code = get_unique_code(json_msg)
        id_assignment = get_id_assigned(json_msg)
        if need_id(self.session.user_id) and id_assignment:
            self.assigned_ids.append((id_assignment,unique_code))
            return

        if self.session.is_host and need_id(sender_id):
            self.publish(id_assignment = utils.get_new_id(), unique_code = unique_code)
            return
        
        instr = get_instr(json_msg)
        if msg.topic == self.topic and instr:
            print(instr)
            WORKBENCH.event_generate("RemoteChange", change=instr)
    
    def publish(self, msg = None, id_assignment = None, unique_code =  None):
        send_msg = {
            "id": self.session.user_id,
            "instr": msg,
            "unique_code": unique_code,
            "id_assigned": id_assignment
        }
        print(send_msg)
        mqtt.Client.publish(self, self.topic, payload = json.dumps(send_msg))


    def Connect(self):
        mqtt.Client.connect(self, self.broker, self.port, 60)
        mqtt.Client.subscribe(self, self.topic, qos=self.qos)
    
    def get_sender(self, msg):
        pass

if __name__ == "__main__":

    class Session_temp:
        def __init__(self, name = "John Doe", _id = 10):
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
