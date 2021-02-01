import tkinter as tk

from thonny.plugins.codelive.mqtt_connection import topic_exists

BG = "#EEEEDD"
class JoinSessionDialog(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master, bg = BG)
        self.data = dict()

        Intro = tk.Label(self, 
                        text="Please Provide information needed to start your new CodeLive Session.",
                        bg = BG)
        
        form_frame = tk.Frame(self, bg = BG)

        name_label = tk.Label(form_frame, text = "Your alias", bg = BG)
        self.name_input = tk.Text(form_frame, height= 1, bd = 5)

        session_topic_label = tk.Label(form_frame, text = "Session Topic", bg = BG)
        self.topic_input = tk.Text(form_frame, height= 1, bd = 5)

        self.name_input.bind("<KeyPress>", self.allow_start_name, True)
        self.topic_input.bind("<KeyPress>", self.allow_start_topic, True)

        name_label.grid(row = 0, column = 0, sticky = tk.E)
        self.name_input.grid(row = 0, column = 1, sticky = tk.W, padx = 10, pady = 5)
        
        session_topic_label.grid(row = 1, column = 0, sticky=tk.E)
        self.topic_input.grid(row = 1, column = 1, sticky=tk.W, padx = 10, pady = 5)
        
        button_frame = tk.Frame(self, bg = BG)

        self.start_button = tk.Button(button_frame,
                                  text="Join!",
                                  command=self.cancel_callback,
                                  fg = "green")
        self.start_button["state"] = tk.DISABLED

        cancel_button = tk.Button(button_frame,
                                  text="Cancel",
                                  command=self.cancel_callback,
                                  fg = "red")
        
        self.start_button.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        cancel_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

        Intro.pack(expand=True, padx = 10, pady = 5)
        form_frame.pack(fill=tk.X, expand=True, padx = 10, pady=5)
        button_frame.pack(fill=tk.X, expand=True, padx = 10, pady=5)

    def allow_start_name(self, event):
        name = self.name_input.get("0.0", "end")
        topic = self.topic_input.get("0.0", "end")

        if len(topic.strip()) == 0:
            print("disabling")
            self.start_button["state"] = tk.DISABLED
        else:
            if event.keysym == "BackSpace" and len(name.strip()) == 1:
                print("disabling")
                self.start_button["state"] = tk.DISABLED
            else:
                print("enabling")
                self.start_button["state"] = tk.NORMAL
    
    def allow_start_topic(self, event):
        name = self.name_input.get("0.0", "end")
        topic = self.topic_input.get("0.0", "end")

        if len(name.strip()) == 0:
            print("disabling")
            self.start_button["state"] = tk.DISABLED
        
        else:
            if event.keysym == "BackSpace" and len(topic.strip()) == 1:
                print("disabling")
                self.start_button["state"] = tk.DISABLED
            else:
                print("enabling")
                self.start_button["state"] = tk.NORMAL

    def start_callback(self):
        name = self.name_input.get("0.0", "end").strip()
        topic = self.topic_input.get("0.0", "end").strip()

        # TODO: if topic doesn't exist, raise warning...
        if True: #topic_exists(topic):
            self.data["name"] = name
            self.data["topic"] = topic
            self.destroy()
            pass
        else:
            pass

    def cancel_callback(self):
        self.destroy()

if __name__ == "__main__":

    root = tk.Tk()

    def start_top():
        top = JoinSessionDialog(root)
        root.wait_window(top)
    
    button = tk.Button(root, text = "Test", command = start_top)
    button.pack(padx = 20, pady = 20)
    root.mainloop()
