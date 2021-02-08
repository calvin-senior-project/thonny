import socket
import tkinter as tk
import re
import queue
import os
import heapq
import random

ALL_REGEX = re.compile("[a-zA-Z0-9 ./<>?;:\"\'`!@#$%^&*()\[\]{}_+=|(\\)-,~]")

MIN_FREE_ID = 0
FREE_IDS = []

def get_instruction(event, text, user_id = -1, cursor_pos = "", in_insert = False, debug = False):
    print("V1")
    if debug:
        print(
            "keysym: ",
            event.keysym,
            "\tkeysym_num",
            event.keysym_num,
            "\tmatch:",
            event.keysym == "BackSpace",
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
        instr = "I" + str(random.randint(0, 100000)) + "[" + text.index(tk.INSERT) + "]"

        if user_id == -1:
            instr += event.char
    
    elif event.keysym == "BackSpace":
        pos = text.index(tk.INSERT)

        try:
            col = int(pos[pos.find('.') + 1 :])
            pos = pos[ : pos.find('.') + 1] + str(col - 1)
        except: 
            pass

        instr = "D" + str(random.randint(0, 100000)) + "[" + pos + "]"
    elif event.keysym == "Return":
        pos = text.index(tk.INSERT)
        instr = "R" + str(random.randint(0, 100000)) + "[" + pos + "]"
    elif event.keysym == "Tab":
        instr = "T" + str(random.randint(0, 100000)) + "[" + text.index(tk.INSERT) + "]"
    elif event.keysym == "Delete":
        print("Right Delete")

    if user_id != -1 and instr != None:
        instr += "(" + str(user_id) + "|" + cursor_pos + ")"
        instr += event.char
    
    print(instr)
    return instr

def get_instr_v2(event, is_insert, user_id = -1, debug = False):
    print("V2")
    instr = ""
    if is_insert:
        instr = "I-" + str(random.randint(0, 100000)) + "[" + event.text_widget.index(event.index) + "]"
        
        if user_id != -1:
            instr += "(" + str(user_id) + "|" + event.cursor_after_change + ")"
            instr += event.text
    else:
        if event.index2 != None:
            instr = "D-" + str(random.randint(0, 100000)) + "[" + event.text_widget.index(event.index1) + "!" + event.text_widget.index(event.index2) + "]"
        else:
            instr = "D-" + str(random.randint(0, 100000)) + "[" + event.text_widget.index(event.index1) + "]"
        if user_id != -1 and instr != None:
            instr += "(" + str(user_id) + "|" + event.cursor_after_change + ")"
    
    return instr

def get_new_id():
    global MIN_FREE_ID
    global FREE_IDS

    if len(FREE_IDS) == 0:
        temp = MIN_FREE_ID
        MIN_FREE_ID += 1
        return temp
    
    else:
        return heapq.heappop(FREE_IDS)

def free_id(val):
    heapq.heappush(FREE_IDS, val)

def send_all(sock, lock, msg):
    sock.sendall(bytes(msg, encoding="utf-8"))

def receive_json(sock):
    while True:
        pass

def publish_delete(broadcast_widget, source, cursor_after_change, index1, index2 = None):
    broadcast_widget.event_generate("LocalDelete", 
                                    index1 = source.index(index1),
                                    index2 = source.index(index2) if index2 else None,
                                    text_widget = source,
                                    cursor_after_change = cursor_after_change)

def publish_insert(broadcast_widget, source, cursor_after_change, index, text):
    broadcast_widget.event_generate("LocalInsert", 
                                    index = source.index(index),
                                    text = text,
                                    text_widget = source,
                                    cursor_after_change = cursor_after_change)

def intiialize_documents(doc_list):
    return []
