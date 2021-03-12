import tkinter as tk
from tkinter import ttk
from thonny.plugins.codelive.mqtt_connection import topic_exists

BG = "#EEEEE4"
class JoinSessionDialog(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent, bg = BG)
        self.protocol("WM_DELETE_WINDOW", self.cancel_callback)
        self.title("Join Live Session - Beta")
        self.data = dict()

        frame = ttk.Frame(self)
        
        intro = ttk.Label(frame, 
                        text="Please Provide information needed to join an existing CodeLive Session.")
        
        form_frame = ttk.Frame(frame)

        name_label = ttk.Label(form_frame, text = "Your alias")
        self.name_input = tk.Text(form_frame, height= 1)

        topic_label = ttk.Label(form_frame, text = "Session Topic")
        self.topic_input = tk.Text(form_frame, height= 1)

        broker_label = ttk.Label(form_frame, text = "MQTT Broker")
        self.broker_input = tk.Text(form_frame, height= 1)

        name_label.grid(row = 0, column = 0, sticky = tk.E)
        self.name_input.grid(row = 0, column = 1, sticky = tk.W, padx = 10, pady = 5)
        
        topic_label.grid(row = 1, column = 0, sticky=tk.E)
        self.topic_input.grid(row = 1, column = 1, sticky=tk.W, padx = 10, pady = 5)

        broker_label.grid(row = 2, column = 0, sticky=tk.E)
        self.broker_input.grid(row = 2, column = 1, sticky=tk.W, padx = 10, pady = 5)
        
        button_frame = ttk.Frame(frame)

        start_button = tk.Button(button_frame,
                                  text="Join!",
                                  command=self.join_callback,
                                  fg = "green",
                                  width = 10)

        cancel_button = tk.Button(button_frame,
                                  text="Cancel",
                                  command=self.cancel_callback,
                                  fg = "red",
                                  width = 10)
        
        start_button.pack(side=tk.RIGHT, padx = 5)
        cancel_button.pack(side=tk.LEFT, padx = 5)

        intro.pack(expand=True, padx = 10, pady = 5)
        form_frame.pack(fill=tk.X, expand=True, padx = 10, pady=5)
        button_frame.pack(side = tk.BOTTOM, padx = 10, pady=5)
        
        frame.pack(fill = tk.BOTH, expand = True)

        self.center(parent.winfo_geometry())

    def center(self, parent_geo):
        parent_dim, parent_x, parent_y = parent_geo.split("+")
        parent_w, parent_h = [int(l) for l in parent_dim.split("x")]

        parent_x = int(parent_x)
        parent_y = int(parent_y)

        w = 450
        h = 180

        x = parent_x + (parent_w - w) / 2
        y = parent_y + (parent_h - h) / 2

        self.geometry("%dx%d+%d+%d" % (w, h, x, y))

    def join_callback(self):
        name = self.name_input.get("0.0", "end").strip()
        topic = self.topic_input.get("0.0", "end").strip()
        broker = self.broker_input.get("0.0", "end").strip()

        if self.valid_name(name) and self.valid_connection(topic, broker):
            self.data["name"] = name
            self.data["topic"] = topic
            self.data["broker"] = broker

            self.destroy()

    def cancel_callback(self):
        if tk.messagebox.askokcancel(parent = self,
                                     title = "Cancel Session",
                                     message = "Are you sure you want to cancel joining the CodeLive session?"):
            self.data = None
            self.destroy()
    
    def valid_name(self, s):
        if len(s) < 8:
            tk.messagebox.showerror(parent = self,
                                     title = "Error",
                                     message = "Please provide a name at least 8 characters long.")
            return False
        return True
    
    def valid_connection(self, topic, broker):
        if len(topic) < 12:
            tk.messagebox.showerror(parent = self,
                                     title = "Error",
                                     message = "Please provide a unique topic with more than 12 characters.")
            return False
        
        if len(broker) < 12:
            tk.messagebox.showerror(parent = self,
                                     title = "Error",
                                     message = "Please provide a valid broker.")
            return False

        # TODO: replace with topic_exists(s) when topic_exists's logic is complete
        if False: #topic_exists(topic, broker):
            tk.messagebox.showerror(parent = self,
                                     title = "Error",
                                     message = "The topic doesn't exist. Make sure your topic is spelled correctly.")
            return False
        return True

if __name__ == "__main__":

    root = tk.Tk()

    def start_top():
        top = JoinSessionDialog(root)
        root.wait_window(top)
    
    button = tk.Button(root, text = "Test", command = start_top)
    button.pack(padx = 20, pady = 20)
    root.mainloop()
