import tkinter as tk
from tkinter import ttk

from thonny.plugins.codelive.views.session_status.user_list import UserList, UserListItem

class SessionInfo(ttk.LabelFrame):
    def __init__(self, parent, session):
        ttk.LabelFrame.__init__(self, parent, width = 100, text = "Session Info")
        # labels
        frame = ttk.Frame(self)
        name_label = ttk.Label(frame, text = "Your name: ")
        topic_label = ttk.Label(frame, text = "Topic: ")
        broker_label = ttk.Label(frame, text = "Broker: ")
        driver_label = ttk.Label(frame, text = "Driver: ")

        # feilds
        connection_info = session.get_connection_info()
        print(connection_info)

        self.session = session
        self.driver_name = tk.StringVar()
        self.driver_name.set(session.get_driver())

        name = ttk.Label(frame, text = session.username)
        topic = ttk.Label(frame, text = connection_info["topic"])
        broker = ttk.Label(frame, text = connection_info["broker"])
        driver = ttk.Label(frame, textvariable = self.driver_name)

        # position
        name_label.grid(row = 0, column = 0, sticky = tk.E)
        topic_label.grid(row = 1, column = 0, sticky = tk.E)
        broker_label.grid(row = 2, column = 0, sticky = tk.E)
        driver_label.grid(row = 3, column = 0, sticky = tk.E)

        name.grid(row = 0, column = 1, sticky = tk.W)
        topic.grid(row = 1, column = 1, sticky = tk.W)
        broker.grid(row = 2, column = 1, sticky = tk.W)
        driver.grid(row = 3, column = 1, sticky = tk.W)

        frame.pack(side = tk.TOP, fill = tk.X, expand = True, anchor = tk.CENTER)
    
    def update_driver(self, s = None):
        if s != None:
            self.driver_name.set(s)
        
        else:
            self.driver_name.set(self.session.get_driver()[1])
    
    def update_driver_id(self, _id):
        self.driver_name.set(self.session.get_name(_id))

class ActionList(ttk.Frame):
    def __init__(self, parent, session):
        ttk.Frame.__init__(self, parent)
        self.request_control = tk.Button(self, text = "Request Control", background = "green")
        leave = tk.Button(self, text = "Leave Session", foreground = "orange")
        self.end = tk.Button(self, text = "End Session", foreground = "red")
        
        leave.pack(side = tk.TOP, fill = tk.X, expand = True)
        self.end.pack(side = tk.TOP, fill = tk.X, expand = True, pady = (5, 0))

        self.request_control["state"] = tk.DISABLED if session.is_host else tk.NORMAL
        self.end["state"] = tk.DISABLED if session.is_host else tk.NORMAL
    
    def driver(self, val = None):
        if val == None:
            return self.end["state"] == tk.NORMAL

        self.request_control["state"] = tk.DISABLED if val else tk.NORMAL
        self.end["state"] = tk.DISABLED if val else tk.NORMAL
    
    def toggle_driver(self):
        self.end["state"] = tk.DISABLED if self.end["state"] == tk.NORMAL else tk.NORMAL
        self.request_control["state"] = tk.DISABLED if self.request_control["state"] == tk.NORMAL else tk.NORMAL
        

class SessionDialog(tk.Toplevel):
    def __init__(self, parent, session):
        tk.Toplevel.__init__(self)
        self.title("Current Session")
        frame = ttk.Frame(self)

        self.session = session
        self.session_info = SessionInfo(frame, session)
        sep1 = ttk.Separator(frame, orient = tk.HORIZONTAL)
        self.user_list = UserList(frame, session, text = "Active Users", borderwidth = 1, width = 1000)
        sep2 = ttk.Separator(frame, orient = tk.HORIZONTAL)
        self.buttons = ActionList(frame, session)

        self.session_info.pack(side = tk.TOP, fill = tk.X, expand = True, padx = 10, pady = 5, anchor = tk.CENTER)
        sep1.pack(side = tk.TOP, fill = tk.X, expand= True, padx = 10)
        self.user_list.pack(side = tk.TOP, fill = tk.BOTH, expand = True, padx = 10, pady = (5, 5))
        sep2.pack(side = tk.TOP, fill = tk.X, expand= True, padx = 10)
        self.buttons.pack(side = tk.TOP, fill = tk.X, expand = True, padx = 10, pady = (5, 10))

        frame.pack(fill = tk.BOTH, expand = True)
    
    def update_host(self, _id = None):
        self.user_list.update_driver(_id)
        self.buttons.driver(self.session.is_host)
         
        if _id == None:
            self.session_info.update_driver()
        else:
            self.session_info.update_driver_id(_id)

if __name__ == "__main__":
    import sys
    import random
    import string

    colors = ["#75DBFF", "#50FF56", "#FF8D75", "#FF50AD", "#FF9B47"]

    class DummyUser:
        def __init__(self, _id, is_host = False):
            self.name = "John " + ''.join(random.choice(string.ascii_uppercase) for i in range(10))
            self.id = _id
            self.position = "1.1"
            self.color = random.choice(colors)
            self.last_alive = 0

            self.is_host = is_host
            self.is_idle = False
            self.cursor_colored = True

    class DummySession:
        def __init__(self, is_host = False):
            self._remote_users = {i : DummyUser(i) for i in range(0, 10)}
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
        
        def get_users(self):
            return self._remote_users

    root = tk.Tk()
    dummyUser = DummyUser(random.randint(0, 9), len(sys.argv) > 2 and sys.argv[2] == "host")
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
        frame.pack(fill = tk.BOTH, expand = True)

        def t():
            frame.toggle_driver()

        button = ttk.Button(root, text = "Hey", command = t)
        button.pack()

    elif sys.argv[1] == "list":
        frame = UserList(root, dummySession)
        frame.pack(fill = tk.BOTH, expand = True)

    elif sys.argv[1] == "action":
        frame = ActionList(root, dummySession)
        frame.pack(fill = tk.X, expand = True)

    root.mainloop()