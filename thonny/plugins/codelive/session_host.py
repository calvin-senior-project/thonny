import os
import socket
import socketserver
from threading import Thread, Lock
from queue import SimpleQueue

from thonny import get_workbench
from tkinter import PhotoImage

MSGLEN = 2048
WORKBENCH = get_workbench()

class Host(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._name = "Hi"
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connections = {}
        self._instruction_queue = SimpleQueue()
        self._server.bind(('localhost', 8000))
        self._editor_notebook = WORKBENCH.get_editor_notebook()
        self._end = False

    def receive(self, sock):
        chunk = sock.recv(MSGLEN)
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        return chunk

    def makeChange(self, sock):
        active = True
        while active:
            msg = str(self.receive(sock), encoding="ascii")
            if msg == "END":
                active = False
                print("ENDING")
            else:
                codeview = self._editor_notebook.get_current_editor().get_text_widget()
                print("command: %s\tposition: %s\tsrting: %s" % (msg[0], msg[2:msg.find("]")], msg[msg.find("]") + 1:]))
                if msg[0] == "I":
                    position = msg[2 : msg.find("]")]
                    new_text = msg[msg.find("]") + 1 : ]
                    codeview.insert(position, new_text)
                elif msg[0] == "D":
                    codeview.delete(msg[2:msg.find("]")])
                elif msg[0] == "R":
                    codeview.insert(position, '')
                    codeview.insert(position, '\r')
                elif msg[0] == "T":
                    codeview.insert(position, '\t')
                elif len(msg) >= 5 and msg[0 : 5] == "FIRST":
                    # self.insert_cursor(codeview, msg[6 : msg.find("]")])
                    pass
        sock.shutdown(0)
    
    def insert_cursor(self, editor, pos):
        cursor_image = PhotoImage(os.path.join(os.path.dirname(__file__), "res/cursor.png"))
        editor.image_create(pos, image=cursor_image)

    def end(self):
        self._end = True

    def get_client_color(self):
        # TODO: IMPLEMENT LOGIC TO ASSIGN CLIENT CURSORS A COLOR
        return "blue"

    def run(self):
        self._server.listen(5)

        while self._end == False:
            client, add = self._server.accept()
            print("new connection at:", add)
            new_client = Thread(target=self.makeChange, args=(client, ))
            self._connections["add"] = {"process" : new_client,
                                        "name" : add[0], 
                                        "color" : self.get_client_color(),
                                        }
            new_client.start()
        
        for connection in self._connections:
            print("Connection %s ending..." % (connection))
            if self._connections[connection].isalive():
                self._connections[connection].stop()
        print("-------------------------------------------")
        for connection in self._connections:
            self._connections[connection].join()
            print("Connection %s joined..." % (connection))
            del self._connections[connection]

if __name__ == "__main__":
    # Unit Tests
    pass
