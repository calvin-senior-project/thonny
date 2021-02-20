import copy
import json
import os
import queue
import random
import re
import sys
import threading
import time
import tkinter as tk
import types

from thonny import get_workbench
from thonny.tktextext import EnhancedText
import thonny.plugins.codelive.patched_callbacks as pc
import thonny.plugins.codelive.mqtt_connection as cmqtt
import thonny.plugins.codelive.utils as utils
from thonny.plugins.codelive.remote_user import RemoteUser, USER_COLORS, RemoteUserEncoder

MSGLEN = 2048
SOCK_ADDR = ('localhost', 8000)
WORKBENCH = get_workbench()

class Session:

    def __init__(self, 
                 _id = -1,
                 name = None,
                 topic = None,
                 broker = None,
                 shared_editors = None,
                 is_host = False,
                 is_cohost = False,
                 debug = True):

        self._remote_users = dict()
        self.username = name if name != None else ("Host" if is_host else "Client")
        self.user_id = _id if _id != -1 else utils.get_new_id()
        self._used_ids = []

        # UI handles
        self._editor_notebook = WORKBENCH.get_editor_notebook()
        self._shared_editors = dict() if shared_editors == None else {editor : i for (i , editor) in enumerate(shared_editors)}
        self._active_editor = self._editor_notebook.get_current_editor().get_text_widget()

        # Network handles
        self._connection = cmqtt.MqttConnection(self, broker_url=broker, topic = topic)
        self._network_lock = threading.Lock()

        # client privilage flags
        self.is_host = is_host
        self.is_cohost = is_cohost

        # service threads
        # self._cursor_blink_thread = threading.Thread(target=self._cursor_blink, daemon=True)

        # bindings
        WORKBENCH.bind("RemoteChange", self.apply_remote_changes)
        self._callback_ids = {
            "text": self.bind_events(),
            "cursor": self.bind_cursor_callbacks()
        }
        self.initialized = False
        
        self._default_insert = None
        self._defualt_delete = None

        self._debug = debug

        self.replace_insert_delete()

    @classmethod
    def create_session(cls, name, topic, broker = None, shared_editors = None, debug = False):
        return Session(_id = utils.get_new_id(),
                       name = name,
                       topic = topic,
                       broker = broker or cmqtt.get_default_broker(),
                       shared_editors = shared_editors,
                       is_host = True)

    @classmethod
    def join_session(cls, name, topic, broker, debug = False):
        current_state = cmqtt.MqttConnection.handshake(name, topic, broker)
        # shared_editors = utils.intiialize_documents(current_state["docs"])
        
        return Session(_id = current_state["id"],
                       name = current_state["name"],
                       topic = topic,
                       broker = broker,
                       shared_editors = current_state["editors"],
                       is_cohost = current_state["is_cohost"])
    
    def get_new_doc_id(self):
        if self._shared_editors == None:
            return 0
        else:
            existing = sorted(self._shared_editors.keys())
            for i in range(len(existing)):
                if i != existing[i]:
                    return i
            return len(existing)
    
    def get_document_state(self):
        json_form = dict()

        for editor in self._shared_editors:
            temp = {"title": editor.get_title(),
                    "content": editor.get_text_widget().get("0.0", tk.END)}
            json_form[self._shared_editors[editor]] = temp
        
        return json_form
    
    def get_active_users(self, in_json = True):
        if in_json == False:
            return self._remote_users
        
        return RemoteUserEncoder().encode(self._remote_users)

    def replace_insert_delete(self):
        defn_saved = False

        for editor in self._shared_editors:
            widget = editor.get_text_widget()
            
            if not defn_saved:
                self._default_insert = widget.insert
                self._default_delete = widget.delete
                defn_saved = True
            
            widget.insert = types.MethodType(pc.patched_insert, widget)
            widget.delete = types.MethodType(pc.patched_delete, widget)
    
    # For all
    def bind_events(self):
        '''
        Bind keypress binds the events from components with callbacks. The function keys 
        associated with the bindings are returned as values of a dictionary whose keys are string of
        the event sequence and the components name separated by a "|"
        '''

        bind_hash = dict()

        text_widget = get_workbench().get_editor_notebook().get_current_editor().get_text_widget()
        
        bind_hash["<KeyPress>|self._editor_notebook.get_current_editor()"] = text_widget.bind("<KeyPress>", self.broadcast_keypress, True)
        bind_hash["LocalInsert|get_workbench()"] = get_workbench().bind("LocalInsert", self.broadcast_insert, True)
        bind_hash["LocalDelete|get_workbench()"] = get_workbench().bind("LocalDelete", self.broadcast_delete, True)
        
        return bind_hash

    def _cursor_blink(self):
        while True:
            time.sleep(0.5)
            text_widget = self._editor_notebook.get_current_editor().get_text_widget()

            for i in text_widget.tag_names():
                if i != str(self.user_id) and i in self._remote_users:
                    if self._remote_users[i].cursor_colored:
                        text_widget.tag_config(i, background="white")
                        self._remote_users[i].cursor_colored = False
                    else:
                        text_widget.tag_config(i, background=self._remote_users[i].color)
                        self._remote_users[i].cursor_colored = True

    def send(self, msg = None):
        self._connection.publish(msg)
    
    def boradcast_cursor_motion(self, event):
        text_widget = self._editor_notebook.get_current_editor().get_text_widget()
        instr = "M(" + str(self.user_id) + "|" + text_widget.index(tk.INSERT) + ")"
        self.send(instr)
    
    def broadcast_insert(self, event):
        instr = utils.get_instr_v2(event, True, user_id = self.user_id)

        if instr == None:
            return

        if self._debug:
            print("*****************\nSending: %s\n*****************" % instr)
        self.send(instr)

    def broadcast_delete(self, event):
        instr = utils.get_instr_v2(event, False, user_id = self.user_id)

        if instr == None:
            return
        
        if self._debug:
            print("*****************\nSending: %s\n*****************" % instr)
        
        self.send(instr)

    def broadcast_keypress(self, event):
        text_widget = self._editor_notebook.get_current_editor().get_text_widget()
        
        instr = utils.get_instruction(event, text_widget, self.user_id, 
                                text_widget.index(tk.INSERT), False)
        
        if instr == None:
            return

        if self._debug:
            print("in broadcast: -%s-" % instr)

        self.send(instr)
    
    def bind_cursor_callbacks(self):
        bind_hash = dict()
        text_widget = self._editor_notebook.get_current_editor().get_text_widget()

        bind_hash["<KeyRelease-Left>|self._editor_notebook.get_current_editor().get_text_widget()"] = text_widget.bind("<KeyRelease-Left>", self.boradcast_cursor_motion, True)
        bind_hash["<KeyRelease-Left>|self._editor_notebook.get_current_editor().get_text_widget()"] = text_widget.bind("<KeyRelease-Right>", self.boradcast_cursor_motion, True)
        bind_hash["<KeyRelease-Left>|self._editor_notebook.get_current_editor().get_text_widget()"] = text_widget.bind("<KeyRelease-Up>", self.boradcast_cursor_motion, True)
        bind_hash["<KeyRelease-Left>|self._editor_notebook.get_current_editor().get_text_widget()"] = text_widget.bind("<KeyRelease-Down>", self.boradcast_cursor_motion, True)
        bind_hash["<KeyRelease-Left>|self._editor_notebook.get_current_editor().get_text_widget()"] = text_widget.bind("<KeyRelease-Return>", self.boradcast_cursor_motion, True)
        bind_hash["<ButtonRelease-1>|self._editor_notebook.get_current_editor().get_text_widget()"] = text_widget.bind("<ButtonRelease-1>", self.boradcast_cursor_motion, True)

        return bind_hash

    def end_broadcast(self):

        for call_type in self._callback_ids:
            id_map = self._callback_ids[call_type]

            for i in id_map:
                event, widget = i.split("|")
                eval(widget).unbind(event, id_map)
    
    def get_connection_info(self):
        return {"name" : self.username,
                "broker" : self._connection.broker,
                "topic" : self._connection.topic}
    
    def get_document_state(self):
        pass

    def get_active_users(self):
        pass
    
    def get_driver(self):
        if self.is_host:
            return "You"
        
        else:
            for i in self._remote_users:
                if self._remote_users[i].is_host == True:
                    return self._remote_users[i].name
        
        return "null"
    
    def get_users(self):
        return self._remote_users
    
    def apply_remote_changes(self, event):
        msg = event.change
        
        codeview = self._editor_notebook.get_current_editor().get_text_widget()
    
        if self._debug:
            print("command: %s" % msg)
        
        if msg[0] in ("I", "D", "R", "T", "M"):
            position = msg[msg.find("[") + 1 : msg.find("]")]

        if msg[0] == "I":
            new_text = msg[msg.find(")") + 1 : ]
            
            tk.Text.insert(codeview, position, new_text)
        
        elif msg[0] == "D":
            if msg.find("!") == -1:
                tk.Text.delete(codeview, msg[msg.find("[") + 1 : msg.find("]")])
            else:
                tk.Text.delete(codeview,
                                msg[msg.find("[") + 1 : msg.find("!")],
                                msg[msg.find("!") + 1 : msg.find("]")])
        
        elif msg[0] == "R":
            if codeview.index(position) == \
                codeview.index(position[:position.find(".")] + ".end"):
                idx = int(position[position.find(".") + 1: ]) + 1
                tk.Text.insert(codeview, 
                                position[:position.find(".") + 1] + str(idx),
                                '\n')
            else:
                tk.Text.insert(codeview, position, '\n')
        
        elif msg[0] == "T":
            tk.Text.insert(codeview, position, '\t')
        
        # if msg[0] in ("I", "D", "R", "T", "M"):
        #     user_id = msg[msg.find("(") + 1 : msg.find("|")]
        #     cur_position = msg[msg.find("|") + 1: msg.find(")")]
        #     self.update_remote_cursor(user_id, cur_position, is_keypress= msg[0] != "M")

    def update_remote_cursor(self, user_id, index, is_keypress = False):
        color = self._remote_users[user_id].color
        text_widget = self._editor_notebook.get_current_editor().get_text_widget()
        
        text_widget.mark_set(user_id, index)

        if user_id in text_widget.tag_names():
            text_widget.tag_delete(user_id)
        
        col = int(index[index.find(".") + 1 : ])
        if col != 0:
            real_index = index[: index.find(".") + 1] + \
                         str(col if is_keypress else col - 1)
            text_widget.tag_add(user_id, real_index)
            text_widget.tag_configure(user_id, background=color)

    def start_session(self):
        self._connection.Connect()
        self._connection.loop_start()

if __name__ == "__main__":
    sess = Session(sys.argv[1] == "host" if len(sys.argv) > 1 else False)
    sess.start_session()
