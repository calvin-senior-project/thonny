import tkinter as tk

from thonny.plugins.codelive.mqtt_connection import generate_topic, topic_exists

BG = "#EEEEDD"
class CreateSessionDialog(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master, bg = BG)
        self.data = dict()

        Intro = tk.Label(self, 
                        text="Please Provide information needed to start your new CodeLive Session.",
                        bg = BG)
        
        form_frame = tk.Frame(self, width = 50, bg = BG)

        name_label = tk.Label(form_frame, text = "Your alias", bg = BG)
        self.name_input = tk.Text(form_frame, height= 1, bd = 5)

        session_topic_label = tk.Label(form_frame, text = "Session Topic", bg = BG)
        self.topic_input = tk.Text(form_frame, height= 1, bd = 5)

        self.auto_gen_topic_state = tk.IntVar()
        self.auto_generate_check = tk.Checkbutton(form_frame, 
                                                  text = "Auto-generate", 
                                                  command = self.auto_gen_callback,
                                                  variable = self.auto_gen_topic_state,
                                                  onvalue = 1,
                                                  offvalue = 0)

        self.name_input.bind("<KeyPress>", self.allow_start_name, True)
        self.topic_input.bind("<KeyPress>", self.allow_start_topic, True)

        name_label.grid(row = 0, column = 0, sticky = tk.E)
        self.name_input.grid(row = 0, column = 1, sticky = tk.W, padx = 10, pady = 5)
        
        session_topic_label.grid(row = 1, column = 0, sticky=tk.E)
        self.topic_input.grid(row = 1, column = 1, sticky=tk.W, padx = 10, pady = 5)
        self.auto_generate_check.grid(row = 1, column = 3, sticky = tk.E)

        button_frame = tk.Frame(self, bg = BG)

        self.start_button = tk.Button(button_frame,
                                  text="Start!",
                                  command=self.start_callback,
                                  fg = "green")
        self.start_button["state"] = tk.DISABLED

        cancel_button = tk.Button(button_frame,
                                  text="Cancel",
                                  command=self.cancel_callback,
                                  fg = "red")
        
        self.start_button.pack(side=tk.RIGHT, fill=tk.X, expand = True)
        cancel_button.pack(side=tk.LEFT, fill=tk.X, expand = True)

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

        if topic_exists(topic):
            # TODO: if the topic exists
            pass
        else:
            # Check if there's an existing session with a similar name
            self.data["name"] = name
            self.data["topic"] = topic
            self.destroy()

    def cancel_callback(self):
        self.destroy()
    
    def auto_gen_callback(self):
        print("exx: ", self.auto_gen_topic_state.get())
        if self.auto_gen_topic_state.get() == 0:
            self.topic_input["state"] = tk.NORMAL
        else:
            n = generate_topic()
            print("gen-ed:", n)
            tk.Text.delete(self.topic_input, "0.0", "end")
            tk.Text.insert(self.topic_input, "0.0", n)
            self.topic_input["state"] = tk.DISABLED

if __name__ == "__main__":

    root = tk.Tk()

    def start_top():
        top = CreateSessionDialog(root)
        root.wait_window(top)
    
    button = tk.Button(root, text = "Test", command = start_top)
    button.pack(padx = 20, pady = 20)
    root.mainloop()
