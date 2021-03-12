import json
import uuid
import paho.mqtt.client as mqtt_client
import paho.mqtt.publish as mqtt_publish
import paho.mqtt.subscribe as mqtt_subscribe
import tkinter as tk
import time

from thonny import get_workbench

import thonny.plugins.codelive.mqtt_connection as mqttc


def get_sender_id(json_msg):
    return json_msg['id']

def get_instr(json_msg):
    return json_msg['instr']


class MqttUserManagement(mqtt_client.Client):
    def __init__(self, 
                 session,
                 broker_url, 
                 port, 
                 qos, 
                 delay, 
                 topic,
                 on_message = None,
                 on_publish = None,
                 on_connect = None):
        mqtt_client.Client.__init__(self)
        self.session = session
        self.broker = broker_url
        self.port = port
        self.qos = qos
        self.delay = delay
        self.users_topic = topic + "/" + "UserManagement"

    def print_something(self):
        print(self.broker, "Hello Nerd")

    def Connect(self):
        mqtt_client.Client.connect(self, self.broker, self.port, 60)
        mqtt_client.Client.subscribe(self, self.users_topic, qos=self.qos)
        mqtt_client.Client.subscribe(self, self.users_topic + "/" + str(self.session.user_id), qos=self.qos)

    def on_message(self, client, data, msg):
        json_msg = json.loads(msg.payload)
        sender_id = get_sender_id(json_msg)

        if sender_id == self.session.user_id:
            print(sender_id,"It's me", "instr ignored")
            return
   
        if json_msg['type'] == 'request_control':
            if tk.messagebox.askokcancel(parent = get_workbench(),
                                     title = "Control Request",
                                     message = "Make " + json_msg['name'] + " host?"): #add a timeout on this?
                self.respond_to_request(json_msg, True) 
        
        if json_msg['type'] == 'request_give':
            if tk.messagebox.askokcancel(parent = get_workbench(),
                                     title = "Control Request",
                                     message = "Accept host-handoff from " + json_msg['name'] + "?"): #add a timeout on this?
                self.respond_to_request(json_msg, True) 
                

    
    def publish(self, msg = None, id_assignment = None, unique_code =  None):
        send_msg = {
            "id": self.session.user_id,
            "instr": msg
        }
        mqtt_client.Client.publish(self, self.users_topic, payload = json.dumps(send_msg))


    def request_give(self,targetID, timeout):
        time.sleep(30)
        if targetID not in self.session._users or targetID == self.session.user_id:
            return 3
        reply_url = str(uuid.uuid4())
        request = {
            "id" : str(self.session.user_id),
            "name": self.session.name,
            "reply": reply_url,
            "type": "request_give"
        }
        print("request_give")
        mqttc.MqttConnection.single_publish(self.users_topic + "/" + str(targetID), json.dumps(request), self.broker)
        payload = mqttc.MqttConnection.single_subscribe(self.users_topic + "/" + reply_url, self.broker, timeout)

        if payload == "":
            return 2
        try:
            response = json.loads(payload)
            if response['id'] == str(self.session.user_id) and response['approved'] == True:
                print("yes")
                return 0
            elif response['id'] == str(self.session.user_id) and response['approved'] == False:
                return 1
        except Exception:
            pass
        return 3
    
    def respond_to_give(self,json_msg, approved):
        response = {
            "id" : json_msg["id"],
            "approved": approved,
            "type": "request_give"
        }
        print("Responding...")
        mqtt_publish.single(self.users_topic + "/" + json_msg["reply"], payload= json.dumps(response), hostname = self.broker)

    def request_control(self, timeout):
        host_id, host_name = self.session.get_driver()
        if host_id in {-1, self.session.user_id}:
            return 3
        reply_url = str(uuid.uuid4())
        request = {
            "id" : str(self.session.user_id),
            "name": self.session.name,
            "reply": reply_url,
            "type": "request_control"
        }

        mqttc.MqttConnection.single_publish(self.users_topic + "/" + str(host_id), json.dumps(request), self.broker)
        payload = mqttc.MqttConnection.single_subscribe(self.users_topic + "/" + reply_url, self.broker, timeout)

        if payload == "":
            return 2
        try:
            response = json.loads(payload)
            if response['id'] == str(self.session.user_id) and response['approved'] == True:
                print("yes")
                return 0
            elif response['id'] == str(self.session.user_id) and response['approved'] == False:
                return 1
        except Exception:
            pass
        return 3


    def respond_to_request(self, json_msg, approved):
        response = {
            "id" : json_msg["id"],
            "approved": approved,
            "type": "request_control"
        }

        mqtt_publish.single(self.users_topic + "/" + json_msg["reply"], payload= json.dumps(response), hostname = self.broker)



        
