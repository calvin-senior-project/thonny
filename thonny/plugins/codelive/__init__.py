
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

import thonny.plugins.codelive.patched_callbacks as pc

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
    global session
    if session != None:
        session.end()
        if DEBUG:
            print("Session end flag set")
        session = None
    else:
        session_type, code = start_session()
        if DEBUG:
            print("session type: %s\tcode: %d" % (session_type, code))

    widget = get_workbench().get_editor_notebook().get_current_editor().get_text_widget()
    widget.insert = types.MethodType(pc.patched_insert, widget)
    widget.delete = types.MethodType(pc.patched_delete, widget) 

def bounce_insert(event):
    print("Insert bounce:\n\tindex: %s\n\ttext:%s" % (event.index, repr(event.text)))

def bounce_delete(event):
    print("Delete bounce:\n\tindex1: %s\n\tindex2: %s" % (event.index1, event.index2))

def inserter():
    get_workbench().get_editor_notebook().get_current_editor().get_text_widget().insert("1.0", "howdy")    

def load_plugin():
    WORKBENCH.add_command(command_id = "add_randomItem",
                          menu_name = "CodeLive",
                          command_label = "Start a Live Collaboration Session",
                          handler = toolbar_callback,
                          position_in_group="end",
                          image=os.path.join(os.path.dirname(__file__), "res/people-yellow-small.png"),
                          caption = "CodeLive",
                          include_in_toolbar = True,
                          bell_when_denied = True)
    
    WORKBENCH.add_command(command_id = "add_random_Item",
                          menu_name = "Code",
                          command_label = "Start a Live Collaboration Session",
                          handler = inserter,
                          position_in_group="end",
                          caption = "CodeLiv",
                          include_in_toolbar = True,
                          bell_when_denied = True)

    # EnhancedText.perform_smart_backspace = pc.patched_perform_smart_backspace
    # EnhancedText.perform_smart_tab = pc.patched_perform_smart_tab
    # EnhancedText.perform_midline_tab = pc.patched_perform_smart_tab
    # EnhancedText._change_indentation = pc.patched_change_indentation
    # EnhancedText._set_region = pc.patched_set_region
    SyntaxText.insert = pc.patched_insert
    SyntaxText.delete = pc.patched_delete
    
    WORKBENCH.bind("LocalInsert", bounce_insert)
    WORKBENCH.bind("LocalDelete", bounce_delete)
