import socket
import tkinter as tk
import re
import queue
import os
import time
import threading
import json
import random
import copy
import sys

from thonny.plugins.codelive.mqtt_connection import *
from thonny.plugins.codelive.utils import get_instruction, get_instr_v2, get_new_id, free_id
from thonny.plugins.codelive.remote_user import RemoteUser, USER_COLORS
from thonny import get_workbench

MSGLEN = 2048
SOCK_ADDR = ('localhost', 8000)
WORKBENCH = get_workbench()

class Session:

    def __init__(self, name = None, topic = None, shared_editors = None, is_host = False, is_cohost = False):
        self._remote_users = dict()
        self._name = name if name != None else ("Host" if is_host else "Client")

        # UI handles
        self._editor_notebook = WORKBENCH.get_editor_notebook()
        self._shared_editors = [] if shared_editors == None else shared_editors
        self._active_editor = self._editor_notebook.get_current_editor().get_text_widget()

        # Network handles
        # self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connection = MqttConnection(self._name, topic = topic)
        self.network_lock = threading.Lock()

        # client privilage flags
        self.is_host = is_host
        self.is_cohost = is_cohost

        # daemon threads
        # self._cursor_blink_thread = threading.Thread(target=self._cursor_blink, daemon=True)
        # self.host_thread = threading.Thread(target=self.accept_connections, daemon=True)

        # bindings
        WORKBENCH.bind("RemoteChange", self.apply_remote_changes)
        self._callback_ids = {
            "text": self.bind_events(),
            "cursor": self.bind_cursor_callbacks()
        }
        
        # for hosting with sockets
        # self._max_connections = 5
        # self.connections = dict()

        # For clients
        # self.receiver_thread = threading.Thread(target=self.receive, args=(self.socket_lock, ), daemon=True)
        self.my_id = get_new_id()
        self.initialized = False

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

    # def _cursor_blink(self):
    #     while True:
    #         time.sleep(0.5)
    #         text_widget = self._editor_notebook.get_current_editor().get_text_widget()

    #         for i in text_widget.tag_names():
    #             if i != str(self.my_id) and i in self._remote_users:
    #                 if self._remote_users[i].cursor_colored:
    #                     text_widget.tag_config(i, background="white")
    #                     self._remote_users[i].cursor_colored = False
    #                 else:
    #                     text_widget.tag_config(i, background=self._remote_users[i].color)
    #                     self._remote_users[i].cursor_colored = True

    def send(self, msg = None):
        # lock.aquire()
        self._connection.publish(msg)
        # lock.release()
    
    # def receive(self, conn):
    #     sock = self.connections[conn]["socket"] if self.is_host else self._sock
        
    #     partial_msg = None
    #     full_msg_len = 0

    #     while True:
    #         chunk = sock.recv(MSGLEN)

    #         if chunk == b'':
    #             print("Connection with", conn, "ended")
    #             break
    #         else:
    #             msg = str(chunk, encoding="utf-8")
    #             print("received:", msg)
                 
    #             if partial_msg == None and len(msg) >= 5 and msg[0 : 5] == "FIRST" and self.initialized == False:
    #                 full_msg_len = int(msg[msg.find("[") + 1 : msg.find("]")])
    #                 self.my_id = int(msg[msg.find("(") + 1 : msg.find(")")])
    #                 partial_msg = msg[msg.find(")") + 1:]
    #                 print("First msg\nlen:", full_msg_len, "\t id:,", self.my_id, "\n part:\n", partial_msg)
                    
    #                 if len(partial_msg) == full_msg_len:
    #                     if len(partial_msg) > 0:
    #                         WORKBENCH.event_generate("RemoteChange", change="I[0.0]" + partial_msg)
    #                         print("I[0.0]" + partial_msg)
    #                     partial_msg = None
    #                     full_msg_len = 0
    #                     self.initialized = True
                
    #             if partial_msg == None:
    #                 WORKBENCH.event_generate("RemoteChange", change=msg)
    #                 print("Pushed -%s- to queue" % msg)
    #             else:
    #                 partial_msg += msg
    #                 print("part:\n", partial_msg)
    #                 if len(partial_msg) == full_msg_len:
    #                     WORKBENCH.event_generate("RemoteChange", change="I[0.0]" + partial_msg)
    #                     print("I[0.0]" + partial_msg)
    #                     partial_msg = None
    #                     full_msg_len = 0
    #                     self.initialized = True
    
    def boradcast_cursor_motion(self, event):
        text_widget = self._editor_notebook.get_current_editor().get_text_widget()
        instr = "M(" + str(self.my_id) + "|" + text_widget.index(tk.INSERT) + ")"
        self.send(instr)
    
    def broadcast_insert(self, event):
        instr = get_instr_v2(event, True, user_id = self.my_id)

        if instr == None:
            return

        print("*****************\nSending: %s\n*****************" % instr)
        self.send(instr)

    def broadcast_delete(self, event):
        instr = get_instr_v2(event, False, user_id = self.my_id)

        if instr == None:
            return
        
        print("*****************\nSending: %s\n*****************" % instr)
        self.send(instr)

    def broadcast_keypress(self, event):
        text_widget = self._editor_notebook.get_current_editor().get_text_widget()
        
        instr = get_instruction(event, text_widget, self.my_id, 
                                text_widget.index(tk.INSERT), False)
        
        if instr == None:
            return

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
    
    def apply_remote_changes(self, event):
        msg = event.change
        
        codeview = self._editor_notebook.get_current_editor().get_text_widget()
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
        # if self.is_host:
        #     self.host_thread.start()
        # else:
        #     while True:
        #         try:
                    
        #             break
        #         except:
        #             print("connection failed... pinging again in 2 secs")
        #             time.sleep(2)
            
        #     self.receiver_thread.start()
        self._connection.Connect()
        self._connection.loop_start()
    # for host
    # def broadcast_host(self, instr):
    #     if instr:
    #         for conn in self.connections:
    #             sock = self.connections[conn]["socket"]
    #             lock = self.connections[conn]["lock"]
    #             self.send(instr)
    
    # def accept_connections(self):
    #     self._sock.bind(SOCK_ADDR)
    #     self._sock.listen(self._max_connections)
        
    #     while True:
    #         client, add = self._sock.accept()
    #         print("New connection at:", add)

    #         handler_lock = threading.Lock()
    #         handler_thread = threading.Thread(target=self.receive, args=(add, ))
    #         author_id = get_new_id()

    #         new_user = RemoteUser(author_id, "", random.sample(USER_COLORS, 1))

    #         self.connections[add] = {"author_id": author_id,
    #                                  "handler_thread" : handler_thread,
    #                                  "lock" : handler_lock,
    #                                  "socket": client}

    #         self.send_current_state(author_id, add)
    #         self._remote_users[str(author_id)] = new_user
    #         handler_thread.start()
            
    #         print("Users:\n", self._remote_users)
        
    # def send_current_state(self, user_id, conn):
    #     sock = self.connections[conn]["socket"]
    #     lock = self.connections[conn]["lock"]
    #     text_widget = self._editor_notebook.get_current_editor().get_text_widget()

    #     full_text = text_widget.get("0.0", tk.END)
    #     if full_text == "\n":
    #         full_text = ""
    #     msg = "FIRST[" + str(len(full_text)) + "]" + \
    #                "(" + str(user_id) + ")" + full_text

    #     lock.acquire()
    #     sock.sendall(bytes(msg, encoding="utf-8"))
    #     lock.release()
    
    # def send_active_users(self, user_list, lock, sock):
    #     list_json = json.dumps(user_list)
    #     self.send(sock, lock, list_json)

if __name__ == "__main__":
    sess = Session(sys.argv[1] == "host" if len(sys.argv) > 1 else False)
    sess.start_session()
