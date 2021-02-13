import tkinter as tk
from tkinter import ttk

from thonny.plugins.codelive.views.session_status.user_list import UserList, UserListItem

class SessionInfo(ttk.Frame):
    def __init__(self, parent, session):
        ttk.Frame.__init__(self, parent)
        # labels
        name_label = ttk.Label(self, text = "Your name: ")
        topic_label = ttk.Label(self, text = "Topic: ")
        broker_label = ttk.Label(self, text = "Broker: ")
        driver_label = ttk.Label(self, text = "Driver: ")

        # feilds
        connection_info = session.get_connection_info()
        print(connection_info)

        self.driver_name = tk.StringVar()
        self.driver_name.set(session.get_driver())

        name = ttk.Label(self, text = session.username)
        topic = ttk.Label(self, text = connection_info["topic"])
        broker = ttk.Label(self, text = connection_info["broker"])
        driver = ttk.Label(self, textvariable = self.driver_name)

        # position
        name_label.grid(row = 0, column = 0, sticky = tk.E)
        topic_label.grid(row = 1, column = 0, sticky = tk.E)
        broker_label.grid(row = 2, column = 0, sticky = tk.E)
        driver_label.grid(row = 3, column = 0, sticky = tk.E)

        name.grid(row = 0, column = 1, sticky = tk.W)
        topic.grid(row = 1, column = 1, sticky = tk.W)
        broker.grid(row = 2, column = 1, sticky = tk.W)
        driver.grid(row = 3, column = 1, sticky = tk.W)
    
    def update_driver(self, s):
        self.driver_name.set(s)

class ActionList(ttk.Frame):
    def __init__(self, parent, session):
        pass 

class SessionDialog(tk.Toplevel):
    def __init__(self, parent, session):
        tk.Toplevel.__init__(self)
        self.title("Current Session")
        frame = ttk.Frame(parent)

        self.session_info = SessionInfo(frame, session)
        self.user_list = UserList(frame, session)
        self.buttons = ActionList(frame, session)

        self.session_info.pack(side = tk.TOP)
        self.user_list.pack(side = tk.TOP)
        self.buttons.pack(side = tk.TOP)

if __name__ == "__main__":
    import sys
    import random
    import string

    colors = ["#75DBFF", "#50FF56", "#FF8D75", "#FF50AD", "#FF9B47"]

    class DummyUser:
        def __init__(self, is_host = False):
            self.name = "John " + ''.join(random.choice(string.ascii_uppercase) for i in range(10))
            self.author_id = random.randint(0, 100)
            self.position = "1.1"
            self.color = random.choice(colors)
            self.last_alive = 0

            self.is_host = is_host
            self.is_idle = False
            self.cursor_colored = True

    class DummySession:
        def __init__(self, is_host = False):
            self._remote_users = {i : DummyUser() for i in range(0, 10)}
            self.username = "John Doe"
            self.is_host = is_host

            if self.is_host == False:
                self._remote_users[random.randint(0, 9)].is_host = True

        def get_connection_info(self):
            return {"name" : self.username,
                    "broker" : "test_broker",
                    "topic" : "test_topic"}
        
        def get_driver(self):
            if self.is_host:
                return "You"
            
            else:
                for i in self._remote_users:
                    if self._remote_users[i].is_host == True:
                        return self._remote_users[i].name
            
            return "null"

    root = tk.Tk()
    dummyUser = DummyUser(len(sys.argv) > 2 and sys.argv[2] == "host")
    dummySession = DummySession(len(sys.argv) > 2 and sys.argv[2] == "host")

    if sys.argv[1] == "dialog":
        def t():
            r = SessionDialog(root, dummySession)

        button = ttk.Button(root, text = "Hey", command = t)
        button.pack()

    elif sys.argv[1] == "info":
        frame = SessionInfo(root, dummySession)
        frame.pack(padx = 50, pady = 50)

    elif sys.argv[1] == "item":
        frame = UserListItem(root, dummyUser)
        frame.pack()
    
    elif sys.argv[1] == "list":
        frame = UserList(root, dummySession)
        frame.pack()

    elif sys.argv[1] == "action":
        frame = ActionList(root, dummySession)
        frame.pack()

    root.mainloop()