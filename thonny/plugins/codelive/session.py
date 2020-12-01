import socket
import tkinter as tk
import re
import queue
import os
import threading

from thonny import get_workbench
from tkinter import PhotoImage

MSGLEN = 2048
WORKBENCH = get_workbench()

MSGLEN = 2048
SOCK_ADDR = ('localhost', 8000)

class Session:
    def __init__(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self._window, self._text_widget = self.create_window()
        self._editor_notebook = WORKBENCH.get_editor_notebook()
        self._active_editor = self._editor_notebook.get_current_editor().get_text_widget()
        self._instruction_queue = queue.SimpleQueue()
        self._text_callback = []
        self._change_thread = threading.Thread(target=self.apply_remote_changes, daemon=True)
    
    def send(self, sock, lock, msg):
        #lock.acquire()
        sent = sock.send(bytes(msg, 'ascii'))
        #lock.release()
        if sent == 0:
            raise RuntimeError("socket connection broken")
    
    def end(self):
        pass

    def end_broadcast(self):
        if len(self._text_callback):
            for hash_val in self._text_callback:
                self._editor_notebook.unbind("<KeyPress>", hash_val)
        self._text_callback = []
    
    def apply_remote_changes(self):
        while True:
            msg = self._instruction_queue.get()
            
            codeview = self._editor_notebook.get_current_editor().get_text_widget()
            print("command: %s\tposition: %s\tsrting: %s" % (msg[0], msg[2:msg.find("]")], msg[msg.find("]") + 1:]))
            
            if msg[0] in ("I", "D", "R", "T"):
                position = msg[2 : msg.find("]")]

            if msg[0] == "I":
                new_text = msg[msg.find("]") + 1 : ]
                codeview.insert(position, new_text)
            elif msg[0] == "D":
                codeview.delete(msg[2:msg.find("]")])
            elif msg[0] == "R":
                if codeview.index(position) == \
                   codeview.index(position[:position.find(".")] + ".end"):
                    idx = int(position[position.find(".") + 1: ]) + 1
                    codeview.insert(position[:position.find(".") + 1] + str(idx), '\n')
                else:
                    codeview.insert(position, '\n')
            elif msg[0] == "T":
                codeview.insert(position, '\t')
    
    def insert_cursor(self, editor, pos):
        cursor_image = PhotoImage(os.path.join(os.path.dirname(__file__), "res/cursor.png"))
        editor.image_create(pos, image=cursor_image)
    
    def start_session(self):
        self._change_thread.start()
        # self._window.mainloop()

if __name__ == "__main__":
    sess = Session()
    sess.start_session()
