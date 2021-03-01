from datetime import datetime
from threading import Lock
import json

USER_COLORS = {"#75DBFF", "#50FF56", "#FF8D75", "#FF50AD", "#FF9B47"}

class RemoteUser:
    def __init__(self, _id, name, color, doc_id, position = "0.0"):
        self.name = name
        self.id = _id
        self.doc_id = doc_id 
        self.position = position
        self.color = color
        self.last_alive = 0

        self.is_idle = False
        self.cursor_colored = True

        self._lock = Lock()

    def set_alive(self):
        with self._lock:
            self.last_live = 0
            self.is_idle = False

    def age(self):
        with self._lock:
            self.last_alive += 1
            
            if self.last_alive > 5:
                self.is_idle = True
                return True
            else:
                return False

    def position(self, doc_id = None, position = None):
        if position and doc_id:
            if doc_id:
                with self._lock:
                    self.doc_id = doc_id

            if position:
                with self._lock:
                    self.position = position
        else:
            with self._lock:
                return self.doc_id, self.position

class RemoteUserEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, RemoteUser):
            return {
                "name": o.name,
                "id": o.id,
                "position": o.position,
                "color" : o.color
            }
            
        else:
            return super().default(o)
