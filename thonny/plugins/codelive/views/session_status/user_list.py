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

            if val and self.make_driver_button.winfo_ismapped():
                    self.make_driver_button.forget()
            elif not self.make_driver_button.winfo_ismapped():
                self.make_driver_button.pack(side = tk.RIGHT, padx = 10)


class UserList(ttk.Frame):
    def __init__(self, parent, session):
        self.scrollable_frame = ScrollableFrame(self)
        self.users = session.get_users()
        self.widgets = self.populate_list(self)
        self.driver = session.get_driver()

        self.scrollable_frame.pack(fill = tk.BOTH, expand = True)

    def populate_list(self):
        for i in self.users:
            self.add_user(self.users[i])

    def add_user(self, user):
        line = UserList(self.scrollable_frame.get_list(), user)
        self.scrollable_frame.append(line)
        self.widgets[user.author_id] = line

    def remove_user(self, user):
        self.remove_id(user.author_id)
    
    def remove_id(self, _id):
        if _id == self.driver:
            return
        self.scrollable_frame.remove_widget(self.widgets[_id])

    def get_driver(self):
        return self.driver
    
    def set_driver(self, user):
        # set new driver
        self.widgets[user.author_id].is_driver(True)
        self.driver = user.author_id
        # remove current driver
        if self.driver >= 0:
            self.widgets[self.driver].is_driver(False)