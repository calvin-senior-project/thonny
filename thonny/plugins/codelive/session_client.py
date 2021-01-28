import queue
import re
import socket
from threading import Thread
import tkinter as tk

from thonny import get_workbench

WORKBENCH = get_workbench()
KEYBOARD_MATCH = "[a-zA-Z0-9(\\t)(\r) ./<>?;:\"\'`!@#$%^&*()\[\]{}_+=|(\\)-,~]"

class Client(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._name = ""
        self.change_queue = queue.SimpleQueue()
        self._sock = None
        self._editors = WORKBENCH.get_editor_notebook()
        self._regex = re.compile(KEYBOARD_MATCH)
        
        self._keygrab_funcID = self._editors.bind("<KeyPress>", self.keypress, True)
        self._end_cmd_funcID = self._editors.bind("<Meta_L>-<Control_L>-<Shift_L>-E", self.end, True)
        
        self._stop = False
    
    def keypress(self, key):
        codeview = self._editors.get_current_editor().get_text_widget()

        if self._regex.match(key.char):
            instr = "I[" + codeview.index(tk.CURRENT) + "]" + key.char
            self.change_queue.put(instr)
        elif key.keysym == "BackSpace":
            print("Left Delete")
        elif key.keysym == "Delete":
            print("Right Delete")

    def run(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect('localhost', 8000)

        while True:
            try:
                next_instr = self.change_queue.get(block=True, timeout=20)
            except queue.Empty:
                if self._stop:
                    break
                else:
                    continue
            sent = self._sock.send(next_instr)
            if sent == 0:
                self.end()
                break
        
        self._sock.shutdown(0)
        self._sock = None

    def end(self):
        if self._keygrab_funcID:
            self._editors.unbind("Keypress", self._keygrab_funcID)
            self._keygrab_funcID = None
        if self._end_cmd_funcID:
            self._editors.unbind("<Meta_L>-<Control_L>-<Shift_L>-E", self._end_cmd_funcID)
            self._end_cmd_funcID = None
        self._stop = True

if __name__ == "__main__":
    # Unit Tests
    pass
