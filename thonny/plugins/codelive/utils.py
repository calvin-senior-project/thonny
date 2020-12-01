import socket
import tkinter as tk
import re
import queue
import os

ALL_REGEX = re.compile("[a-zA-Z0-9 ./<>?;:\"\'`!@#$%^&*()\[\]{}_+=|(\\)-,~]")

def get_instruction(event, text, debug = False):
    if debug:
        print(
            "keysym: ",
            event.keysym,
            "\tkeysym_num",
            event.keysym_num,
            "\tmatch:",
            event.keysym == "BackSpace", # all_regex.match(event.char),
            "\tcurrent:",
            text.index(tk.CURRENT),
            "- c:",
            repr(text.get(text.index(tk.CURRENT))),
            "\tinsert:",
            text.index(tk.INSERT),
            "- c:",
            repr(text.get(text.index(tk.INSERT)))
        )
    
    instr = None
    
    if ALL_REGEX.match(event.char):
        instr = "I[" + text.index(tk.INSERT) + "]" + event.char
    elif event.keysym == "BackSpace":
        pos = text.index(tk.INSERT)

        try:
            col = int(pos[pos.find('.') + 1 :])
            pos = pos[ : pos.find('.') + 1] + str(col - 1)
        except:
            pass

        instr = "D[" + pos + "]"
    elif event.keysym == "Return":
        pos = text.index(tk.INSERT)
        instr = "R[" + pos + "]"
    elif event.keysym == "Tab":
        instr = "T[" + text.index(tk.INSERT) + "]"
    elif event.keysym == "Delete":
        print("Right Delete")
    
    return instr
