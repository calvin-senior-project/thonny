from datetime import datetime
from threading import Lock

USER_COLORS = {"#75DBFF", "#50FF56", "#FF8D75", "#FF50AD", "#FF9B47"}

class RemoteUser:
    def __init__(self, author_id, name, color, position = "0.0"):
        self.name = name
        self.author_id = author_id
        self.position = position
        self.color = color
        self.last_alive = 0

        self.is_idle = False
        self.cursor_colored = True

        self._lock = Lock()
    
    def set_alive(self):
        self.last_live = 0
        self.is_idle = False

    def set_idle(self):
        self.last_alive += 1
        
        if self.last_alive > 5:
            self.is_idle = True
            return True
        else:
            return False

    def update_position(self, new_position):
        self.position = new_position
    