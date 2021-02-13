import tkinter as tk
from tkinter import ttk

from thonny import get_workbench
from thonny.plugins.codelive.views.session_status.scrollable_frame import ScrollableFrame

class UserListItem(tk.Frame):
    def __init__(self, parent, user):
        tk.Frame.__init__(self, parent, highlightbackground = "grey")

        self.user_id = user.author_id
        self.color = user.color
        self.username = user.name
        self.is_driver = user.is_host

        self.label_str = tk.StringVar()
        self.label_str.set(self.username)

        icon = self.create_icon()
        name_label = tk.Label(self, width = 25, textvariable = self.label_str, anchor = "w")
        self.make_driver_button = tk.Button(self, text = "Give Control", width = 10, command = self.make_driver)

        icon.pack(side=tk.LEFT, padx = 10)
        name_label.pack(side=tk.LEFT, fill = tk.X, expand = True)

        if self.is_driver:
            self.make_driver_button.pack(side = tk.RIGHT, padx = 10)
        
    def make_driver(self):
        if __name__ != "__main__":
            get_workbench().event_generate("MakeDriver", user = self.user_id)

    def create_icon(self):
        def create_circle(canvas, x, y, r, **kwargs):
            return canvas.create_oval(x-r, y-r, x+r, y+r, **kwargs)

        icon = tk.Canvas(self, width = 30, height = 30)
        create_circle(icon, 17, 17, 10, fill=self.color, outline="")
        return icon
    
    def is_driver(self, val = None):
        if val == None:
            return self.is_driver
        else:
            self.label_str.set(self.username + " (Driver)" if val else self.username)
            self.is_driver = val


class UserList(ttk.Frame):
    def __init__(self, parent, session):
        self.scrollable_frame = ScrollableFrame(self)
        self.session = session

    def add_user(self, user):
        pass

    def remove_user(self, user):
        pass

    def get_driver(self):
        pass
    
    def set_driver(self):
        pass