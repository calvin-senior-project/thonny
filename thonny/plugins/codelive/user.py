from datetime import datetime
from threading import Lock

import json
import random

from thonny.plugins.codelive.res.default_values import COLORS

def get_color(used_colors = None):
    if used_colors == None:
        return random.choice(COLORS)
    
    else:
        if len(used_colors) == len(COLORS):
            raise ValueError("Unable to assign a new color: len(used_colors) == len(COLORS)")

        for i in range(len(COLORS)):
            color = random.choice(COLORS)
            if color not in used_colors:
                return color
        
        raise ValueError("Unable to assign a new color: attempt timed out")

class User:
    def __init__(self, _id, name, doc_id, color = get_color(), is_host = False, position = "0.0"):
        self.name = name
        self.id = _id
        self.color = color

        self.is_host = is_host

        self.doc_id = doc_id 
        self.position = position

        self.last_alive = 0
        self.is_idle = False
        self.cursor_colored = True

        self._lock = Lock()

    def host(self, val = None):
        if val:
            with self._lock:
                self.is_host = val
        else:
            with self._lock:
                return self.is_host

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

class UserEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, User):
            return {
                "name": o.name,
                "id": o.id,
                "position": o.position,
                "color" : o.color,
                "is_host": o.is_host
            }
            
        else:
            return super().default(o)
