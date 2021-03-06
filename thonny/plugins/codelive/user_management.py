import json
import uuid
import paho.mqtt.client as mqtt_client
import paho.mqtt.publish as mqtt_publish
import paho.mqtt.subscribe as mqtt_subscribe
import tkinter as tk

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
        self.reply_topic = None
        self.my_id_topic = self.users_topic + "/" + str(self.session.user_id)

    def Connect(self):
        mqtt_client.Client.connect(self, self.broker, self.port, 60)
        mqtt_client.Client.subscribe(self, self.users_topic, qos=self.qos)
        mqtt_client.Client.subscribe(self, self.my_id_topic, qos=self.qos)

    def on_message(self, client, data, msg):
        try:
            json_msg = json.loads(msg.payload)
        except Exception:
            return
        sender_id = get_sender_id(json_msg)
        if sender_id == self.session.user_id:
            print("instr ignored")
            return

        if msg.topic == self.reply_topic:
            self.handle_confirmation(json_msg)
            
        
        if msg.topic == self.my_id_topic:
            self.handle_permission_rq(json_msg)


    def request_give(self,targetID):
        if targetID not in self.session._users or targetID == self.session.user_id:
            return 3
        if self.reply_topic: #cleanup
            mqtt_client.Client.unsubscribe(self, self.reply_topic)
        self.reply_topic = self.users_topic + "/" + str(uuid.uuid4())
        request = {
            "id" : self.session.user_id,
            "name": self.session.username,
            "reply": self.reply_topic,
            "type": "request_give"
        }
        mqtt_client.Client.subscribe(self,self.reply_topic, qos=self.qos)
        mqttc.MqttConnection.single_publish(self.users_topic + "/" + str(targetID), json.dumps(request), self.broker)
    
    def respond_to_give(self,json_msg, approved):
        response = {
            "id" : self.session.user_id,
            "approved": approved,
            "type": "request_give"
        }
        print(response)
        mqttc.MqttConnection.single_publish(json_msg["reply"], json.dumps(response), self.broker)

    def request_control(self):
        host_id, host_name = self.session.get_driver()
        if host_id in {-1, self.session.user_id}:
            return 3
        if self.reply_topic: #cleanup
            mqtt_client.Client.unsubscribe(self, self.reply_topic)
        self.reply_topic = self.users_topic + "/" + str(uuid.uuid4())
        request = {
            "id" : self.session.user_id,
            "name": self.session.username,
            "reply": self.reply_topic,
            "type": "request_control"
        }

        mqtt_client.Client.subscribe(self,self.reply_topic, qos=self.qos)
        mqttc.MqttConnection.single_publish(self.users_topic + "/" + str(host_id), json.dumps(request), self.broker)


    def respond_to_request(self, json_msg, approved):
        response = {
            "id" : self.session.user_id,
            "approved": approved,
            "type": "request_control"
        }
        mqtt_publish.single(json_msg["reply"], payload= json.dumps(response), hostname = self.broker)

    def handle_confirmation(self, json_msg):
        message =""
        if json_msg['approved']:
            if json_msg["type"] == "request_control":
                self.session.change_host(self.session.user_id)
            else:
                self.session.change_host(json_msg["id"])
            message = "Granted"
        else:
            message = "Denied"
        tk.messagebox.showinfo(title = "Control Request",
                               message = "Control Request " + message)
        mqtt_client.Client.unsubscribe(self, self.reply_topic)
        self.reply_topic = None

    def handle_permission_rq(self,json_msg):
        approve = False
        if json_msg['type'] == 'request_control':
            approve = tk.messagebox.askokcancel(parent = get_workbench(),
                        title = "Control Request",
                        message = "Make " + json_msg['name'] + " host?") #add a timeout on this?
            self.respond_to_request(json_msg, approve)
            
        if json_msg['type'] == 'request_give':
            approve = tk.messagebox.askokcancel(parent = get_workbench(),
                        title = "Control Request",
                        message = "Accept host-handoff from " + json_msg['name'] + "?") #add a timeout on this?
            self.respond_to_give(json_msg, approve)
        
        if approve:
            self.session.change_host(self.session.user_id if json_msg['type'] == 'request_give' else json_msg["id"])
