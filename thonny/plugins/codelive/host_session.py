import os
import socket
import socketserver
from threading import Thread, Lock
from queue import SimpleQueue

from thonny import get_workbench
# from tkinter import PhotoImage

import tkinter as tk
import re
import queue
import time
import threading

from thonny.plugins.codelive.session import Session, SOCK_ADDR, MSGLEN
from thonny.plugins.codelive.utils import get_instruction

class HostSession(Session):
    def __init__(self):
        Session.__init__(self)
        self._name = "Hi"
        self._text_callback = [self._active_editor.bind("<KeyPress>", self.broadcast_keypress, True)]
        self.host_thread = threading.Thread(target=self.start_host, daemon=True)
        self.socket_lock = threading.Lock()
        self._max_connections = 5
        self.connections = dict()

    def broadcast_keypress(self, event):
        codeview = self._editor_notebook.get_current_editor().get_text_widget()
        instr = get_instruction(event, self._active_editor, True)

        if instr:
            for conn in self.connections:
                sock = self.connections[conn]["socket"]
                lock = self.connections[conn]["lock"]
                self.send(sock, lock, instr)
    
    def start_host(self):
        self._sock.bind(SOCK_ADDR)
        self._sock.listen(self._max_connections)
        
        while True:
            client, add = self._sock.accept()
            print("new connection at:", add)
            handler_lock = threading.Lock()
            handler_thread = threading.Thread(target=self.handler, args=(add, ))
            self.connections[add] = {"handler_thread" : handler_thread,
                                     "lock" : handler_lock,
                                     "socket": client}
            handler_thread.start()

    def handler(self, conn):
        sock = self.connections[conn]["socket"]
        #self.send_current_state(conn)

        while True:
            chunk = sock.recv(MSGLEN)

            if chunk == b'':
                print("Connection with", conn, "end")
                break
            else:
                msg = str(chunk, encoding="ascii")
                self._instruction_queue.put(msg)

    def send_current_state(self, conn):
        sock = self.connections[conn]["socket"]
        lock = self.connections[conn]["lock"]

        codeview = self._editor_notebook.get_current_editor().get_text_widget()
        full_text = codeview.get("0.0", tk.END)

        header = "FIRST[" + str(len(full_text)) + "]"
        packet = full_text[:MSGLEN - len(header)]
        self.send(sock, lock, packet)

        last_end = MSGLEN - len(header)
        for _ in range(0, (len(full_text) - len(header)) // MSGLEN):
            packet = full_text[last_end : last_end + MSGLEN]
            self.send(sock, lock, packet)
            last_end = last_end + MSGLEN

    def start_session(self):
        self.host_thread.start()
        super().start_session()

if __name__ == "__main__":
    sess = HostSession()
    sess.start_session()
