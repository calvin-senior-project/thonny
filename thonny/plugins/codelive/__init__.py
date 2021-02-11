
import os
import types
import tkinter as tk

from tkinter.messagebox import showinfo
from tkinter import Message, Button
from tkinter.commondialog import Dialog

from thonny import get_workbench
from thonny.tktextext import EnhancedText, TweakableText
from thonny.codeview import SyntaxText

from thonny.plugins.codelive.client import Session

from thonny.plugins.codelive.start_up_dialog import StartUpWizard
from thonny.plugins.codelive.views.create_session import CreateSessionDialog
from thonny.plugins.codelive.views.join_session import JoinSessionDialog

import thonny.plugins.codelive.patched_callbacks as pc
import thonny.plugins.codelive.utils as utils

WORKBENCH = get_workbench()
session = None
DEBUG = True

def start_session():
    top = StartUpWizard(parent=WORKBENCH)
    WORKBENCH.wait_window(top)

    global session
    if top.get_session_mode() == "Host":
        print("Starting host")
        session = Session(is_host=True)
    elif top.get_session_mode() == "Client":
        print("Starting client")
        session = Session(topic = top.get_topic())
    else:
        return ("null", -1)
    
    session.start_session()
    return (top.get_session_mode(), 0)

def toolbar_callback():
    # global session
    # if session != None:
    #     session.end()
    #     if DEBUG:
    #         print("Session end flag set")
    #     session = None
    # else:
    #     session_type, code = start_session()
    #     if DEBUG:
    #         print("session type: %s\tcode: %d" % (session_type, code))
    utils.str_to_editor("X", "Hello World!")
    

def create_session():
    
    top = CreateSessionDialog(WORKBENCH)
    WORKBENCH.wait_window(top)

    # if top data is none, then the user chose to cancel the session
    if top.data == None:
        return

    session = Session.create_session(name = top.data["name"],
                                     topic = top.data["topic"],
                                     broker = top.data["broker"],
                                     shared_editors = top.data["shared_editors"])
    
    session.start_session()

def join_session():
    top = JoinSessionDialog(WORKBENCH)
    WORKBENCH.wait_window(top)

    #  if top data is none, then the user chose to cancel the session
    if top.data == None:
        return

    session = Session.join_session(name = top.data["name"],
                                   topic = top.data["topic"],
                                   broker = top.data["broker"])

    session.start_session()

def end_session():
    pass

def leave_session():
    pass

def session_status():
    pass

def null_cmd(event):
    print("hi")

def load_plugin():
    
    WORKBENCH.add_command(command_id = "codelive",
                          menu_name = "CodeLive",
                          command_label = "Start a Live Collaboration Session",
                          handler = toolbar_callback,
                          position_in_group="end",
                          image=os.path.join(os.path.dirname(__file__), "res/people-yellow-small.png"),
                          caption = "CodeLive: MQTT based collaboration plugin",
                          #submenu=submenu,
                          include_in_menu= False,
                          include_in_toolbar = True,
                          bell_when_denied = True)
                
    WORKBENCH.add_command(command_id = "codelive_host",
                          menu_name = "CodeLive",
                          command_label = "Create a New Session",
                          handler = create_session,
                          group = 20,
                          position_in_group="end",
                          caption = "End",
                          bell_when_denied = True)
    
    WORKBENCH.add_command(command_id = "codelive_join",
                          menu_name = "CodeLive",
                          command_label = "Join an Existing Session",
                          handler = join_session,
                          group=20,
                          position_in_group="end",
                          caption = "End",
                          bell_when_denied = True)
    
    WORKBENCH.add_command(command_id = "codelive_end",
                          menu_name = "CodeLive",
                          command_label = "End Session",
                          tester = lambda: session,
                          handler = end_session,
                          group=21,
                          position_in_group="end",
                          caption = "End",
                          bell_when_denied = True)
    
    WORKBENCH.add_command(command_id = "codelive_leave",
                          menu_name = "CodeLive",
                          command_label = "Leave Session",
                          tester = lambda: session,
                          handler = leave_session,
                          group=21,
                          position_in_group="end",
                          caption = "End",
                          bell_when_denied = True)
    
    WORKBENCH.add_command(command_id = "codelive_show",
                          menu_name = "CodeLive",
                          command_label = "Show Session Status",
                          handler = session_status,
                          group=23,
                          position_in_group="end",
                          caption = "End",
                          bell_when_denied = True)

    EnhancedText.insert = pc.patched_insert
    EnhancedText.delete = pc.patched_delete
