import json
import uuid
import paho.mqtt.client as mqtt_client
import paho.mqtt.publish as mqtt_publish
import paho.mqtt.subscribe as mqtt_subscribe

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
            self.respond_to_request(json_msg) 
        

       # instr = get_instr(json_msg)
       # if msg.topic == self.users_topic and instr:
           # print(instr, sender_id, "They have joined")
            #WORKBENCH.event_generate("RemoteChange", change=instr)
    
    def publish(self, msg = None, id_assignment = None, unique_code =  None):
        send_msg = {
            "id": self.session.user_id,
            "instr": msg
        }
        mqtt_client.Client.publish(self, self.users_topic, payload = json.dumps(send_msg))

    def give_control(self, give_id):
        pass

    def respond_to_give(self):
        pass

    def request_control(self):
        host_id, host_name = self.session.get_driver()
        print(host_id,host_name)
        if host_id in {-1, self.session.user_id}:
            return
        reply_url = str(uuid.uuid4())
        request = {
            "id" : str(self.session.user_id),
            "reply": reply_url,
            "type": "request_control"
        }

        mqtt_publish.single(self.users_topic + "/" + str(host_id), payload= json.dumps(request), hostname = self.broker)
        payload = mqttc.MqttConnection.single_subscribe(self.users_topic + "/" + reply_url, self.broker, 1)
        #payload = mqtt_subscribe.simple(self.users_topic + "/" + reply_url, hostname=self.broker).payload
        response = json.loads(payload)
        print(response)
        if response['id'] == self.session.user_id and response['approved'] == True:
            print("Sucess")


    def respond_to_request(self, json_msg):
        response = {
            "id" : json_msg["id"],
            "approved": True,
            "type": "request_control"
        }

        mqtt_publish.single(self.users_topic + "/" + json_msg["reply"], payload= json.dumps(response), hostname = self.broker)


        
