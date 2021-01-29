from tkinter import *

class StartUpDialog(Toplevel):
    def __init__(self, master=None, **options):
        super().__init__(master, options)
        self._client_username = ""
        self._host_username = ""
        self._topic_name = ""
        self._auth_token = ""
        self._max_num_users = ""
        self._mode = ""

        self._pages = {"welcome":      self.welcome_page(),
                       "client_page":  self.client_setup(),
                       "host_page":    self.host_setup()}
        
    
    def welcome_page(self):
        page = Frame(master=self,
                     width=100)
        Label(master = page,
              text="Welcome to Codelive!",
              height=30,
              width=30).pack()

        Button(master=page,
               text="Host",
               command=self.set_host).pack()
        Button(master=page,
               text="Client",
               command=self.set_client).pack()
        Button(master=page,
               text="Cancel",
               command=self.destroy).pack()
        page.pack()

        return page
    
    def client_setup(self):
        page = Frame(master=self,
                     width=100)
        frame = LabelFrame(master = page,
              text="Enter the session code",
              height=30,
              width=30)
        
        session_name_entry = Text(master = frame,
                                  width = 50,
                                  height = 1)
        
        session_name_entry.pack()
        frame.pack()

        def done():
            self.topic_name = session_name_entry.get("1.0")
            self._mode = "Client"
            self.destroy()

        Button(master=page,
               text="Done",
               command=done).pack()
        Button(master=page,
               text="Back",
               command=self.set_client).pack()
        Button(master=page,
               text="Cancel",
               command=self.destroy).pack()
        page.pack()

        return ""

    def host_setup(self):
        return ""
    
    def set_client(self):
        self._mode = "Client"
        self.destroy()
    
    def set_host(self):
        self._mode = "Host"
        self.destroy()

    def run(self):
        return {}
    
    def get_session_mode(self):
        return self._mode

    def get_topic(self):
        return self.topic_name

class StartUpWizard(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self._mode = ""
        self._topic_name = ""

        self.current_step = None
        self.steps = {"welcome":      self.welcome_page(),
                      "client:1":  self.client_setup(),
                      "host:1":    self.host_setup()}

        self.button_frame = Frame(self, bd=1, relief="raised")
        self.content_frame = Frame(self)

        self.back_button = Button(self.button_frame, text="<< Back", command=self.back)
        self.next_button = Button(self.button_frame, text="Next >>", command=self.next)
        self.finish_button = Button(self.button_frame, text="Finish", command=self.finish)
        self.cancel_button = Button(self.button_frame, text="Finish", command=self.cancel)

        self.button_frame.pack(side="bottom", fill="x")
        self.content_frame.pack(side="top", fill="both", expand=True)

        self.show_step("welcome")
    
    def show_step(self, step):

        if self.current_step is not None:
            # remove current step
            current_step = self.steps[self.current_step]
            current_step.pack_forget()

        self.current_step = step

        new_step = self.steps[step]
        new_step.pack(fill="both", expand=True)

        if step == "welcome":
            # first step
            self.back_button.pack_forget()
            self.next_button.pack_forget()
            self.cancel_button.pack(side="right")
            self.finish_button.pack_forget()

        elif step == "Client:1":
            # last step
            self.back_button.pack(side="left")
            self.next_button.pack_forget()
            self.finish_button.pack(side="right")

        else:
            # all other steps
            self.back_button.pack(side="left")
            self.next_button.pack(side="right")
            self.finish_button.pack_forget()

    def back(self):
        pass

    def next(self):
        pass

    def finish(self):
        self.destroy()
    
    def cancel(self):
        self.destroy()
    
    def welcome_page(self):
        page = Frame(master=self,
                     width=100)
        Label(master = page,
              text="Welcome to Codelive!",
              height=30,
              width=30).pack()

        Button(master=page,
               text="Host",
               command=self.go_host).pack()
        Button(master=page,
               text="Client",
               command=self.go_client).pack()

        return page
    
    def go_host(self):
        #self.show_step("host:1")
        self._mode = "Host"
        self.destroy()
    
    def go_client(self):
        self.show_step("client:1")
    
    def client_setup(self):
        page = Frame(master=self,
                     width=100)
        frame = LabelFrame(master = page,
              text="Enter the session code",
              height=30,
              width=30)
        
        session_name_entry = Text(master = frame,
                                  width = 50,
                                  height = 1)
        
        session_name_entry.pack()
        frame.pack()

        def done():
            self.topic_name = session_name_entry.get("1.0", "end").strip()
            self._mode = "Client"
            self.destroy()

        Button(master=page,
               text="Done",
               command=done).pack()

        return page

    def host_setup(self):
        page = Frame(master=self,
                     width=100)
        frame = Label(master = page,
              text="Host Setup Place holder",
              height=30,
              width=30)
        
        frame.pack()

        return page
    
    def get_session_mode(self):
        return self._mode

    def get_topic(self):
        return self.topic_name
