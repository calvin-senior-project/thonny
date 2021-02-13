import tkinter as tk
from tkinter import ttk

class ScrollableFrame(ttk.Frame):
    def __init__(self, master=None, *cnf, **kw):
        ttk.Frame.__init__(self, master=master, *cnf, **kw)
        
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.list = tk.Frame(canvas)

        self.list.bind("<Configure>",
                lambda e: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )
        
        canvas.create_window((0, 0), window=self.list, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        self.children = list()
    
    def get_frame(self):
        return self.list

    def append(self, widget):
        self.children.append(widget)
        widget.pack(fill = tk.X, expand = True)
    
    def insert(self, index, widget):
        index_cpy = index
        if index_cpy >= len(self.children):
            self.append(widget)
            return
        
        elif index_cpy < 0:
            self.insert(0, widget)
            return
        
        # forget items below
        for i in range(index, len(self.children)):
            self.chidlren[i].forget()
        
        # insert to list
        self.children.insert(index, widget)

        # repack items
        for i in range(index, len(self.children)):
            self.children[i].pack(fill = tk.X, expand = True)

    
    def remove(self, index):
        if index in self.children:
            self.children[index].forget()
        
        # update indexes
        while index < len(self.children) - 1:
            self.children[index] = self.children[index + 1]
            index += 1
        
        # delete highest index
        del self.children[len(self.children) - 1]