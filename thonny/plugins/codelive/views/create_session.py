import tkinter as tk
from tkinter import ttk

from thonny import get_workbench
from thonny.plugins.codelive.mqtt_connection import generate_topic, topic_exists

if __name__ == "__main__":
    class DummyEditor:
        def __init__(self, title = "untitled", filename = None):
            self.title = title
            self.filename = filename
        
        def get_title(self):
            return self.title
        
        def get_filename(self):
            return self.filename

class EditorSelector(ttk.Frame):
    def __init__(self, parent, active_editors):
        ttk.Frame.__init__(self, parent)
        self.active_editors = active_editors

        label = ttk.Label(self, 
                          text = "Please choose the editors you want to share")
        
        container, self.editorList = self.get_list()

        self.editorList.bind("<<ListboxSelect>>", self.some_binding)

        label.pack(side = tk.TOP)
        container.pack(side = tk.BOTTOM)

    def some_binding(self, event):
        pass 

    def get_list(self):
        container = ttk.Frame(self)

        scrollbar = tk.Scrollbar(container)
        list_widget = tk.Listbox(container,
                                 yscrollcommand = scrollbar.set,
                                 height = 7,
                                 width = 60,
                                 selectmode = tk.MULTIPLE + tk.EXTENDED)
        scrollbar.configure(command = list_widget.yview)

        for item in self.active_editors:
            editor = self.active_editors[item]
            title = editor.get_title()
            filename = editor.get_filename() or "Unsaved"

            if len(filename) + len(title) + 3 > 50:
                filename = "..." + filename[len(filename) - (len(title) + 6):]
            
            label = " %s (%s) " % (title, editor.get_filename() or "Unsaved")
            list_widget.insert(tk.END, label)

        list_widget.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
        scrollbar.pack(side = tk.RIGHT, fill = tk.BOTH, expand = True)

        return container, list_widget

class CreateSessionDialog(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.protocol("WM_DELETE_WINDOW", self.cancel_callback)

        frame = ttk.Frame(self)

        self.data = dict()

        # Connection info
        Intro = ttk.Label(frame, 
                        text="Please provide information needed to start your new CodeLive Session.")
        
        form_frame = ttk.Frame(frame, width = 50)

        name_label = ttk.Label(form_frame, text = "Your alias")
        self.name_input = tk.Text(form_frame, height= 1, width = 50, bd = 5)

        session_topic_label = ttk.Label(form_frame, text = "Session Topic")
        self.topic_input = tk.Text(form_frame, height= 1, width = 50, bd = 5)

        self.auto_gen_topic_state = tk.IntVar()
        self.auto_generate_check = ttk.Checkbutton(form_frame, 
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

        sep1 = ttk.Separator(frame, orient = tk.HORIZONTAL)
        # Shared editors frame
        self.editor_selector = EditorSelector(frame, self.get_active_editors(parent))

        sep2 = ttk.Separator(frame, orient = tk.HORIZONTAL)
        # Bottom Button Frame
        button_frame = ttk.Frame(frame)

        self.start_button = tk.Button(button_frame,
                                  text="Start!",
                                  command=self.start_callback,
                                  fg = "green",
                                  width = 10)
        self.start_button["state"] = tk.DISABLED

        cancel_button = tk.Button(button_frame,
                                  text="Cancel",
                                  command=self.cancel_callback,
                                  fg = "red",
                                  width = 10)
        
        self.start_button.pack(side=tk.RIGHT, fill=tk.X, expand = True, padx = 5)
        cancel_button.pack(side=tk.LEFT, fill=tk.X, expand = True, padx = 5)

        Intro.pack(expand=True, padx = 10, pady = 5)
        form_frame.pack(side = tk.TOP, expand = False, padx = 10, pady=5)
        
        sep1.pack(side = tk.TOP, fill = tk.X, expand= True)
        self.editor_selector.pack(side = tk.TOP, fill = tk.BOTH)
        sep2.pack(side = tk.TOP, fill = tk.X, expand= True)
        
        button_frame.pack(side = tk.BOTTOM, padx = 10, pady=5)
        frame.pack(fill = tk.BOTH, expand = True)

        self.center(parent.winfo_geometry())

    def center(self, parent_geo):
        # TODO: center the top level window
        print(parent_geo)
        
        parent_dim, parent_x, parent_y = parent_geo.split("+")
        parent_w, parent_h = [int(l) for l in parent_dim.split("x")]

        parent_x = int(parent_x)
        parent_y = int(parent_y)

        w = 650 # self.winfo_reqwidth()
        h = 300 # self.winfo_reqheight()

        x = parent_x + (parent_w - w) / 2
        y = parent_y + (parent_h - h) / 2

        self.geometry("%dx%d+%d+%d" % (w, h, x, y))
        pass

    def get_active_editors(self, parent):
        editors = dict()

        # for testing only
        if __name__ == "__main__":
            editors = {0: DummyEditor(),
                        1: DummyEditor("Hello"),
                        2: DummyEditor(filename = "hello path"),
                        3: DummyEditor("Hello", "Hello's path")}
        
        else:
            editors = {index : editor for (index, editor) in enumerate(parent.get_editor_notebook().winfo_children())}

        return editors

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
        if tk.messagebox.askokcancel(parent = self,
                                     title = "Cancel Session",
                                     message = "Are you sure you want to cancel hosting a CodeLive session?"):
            self.data = None
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
