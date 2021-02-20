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
                    scrollregion=canvas.bbox("all"),
                    # width = max([x["width"] for x in self.list_children])
                )
            )
        
        canvas.create_window((0, 0), window=self.list, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        self.list_children = list()

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def get_frame(self):
        return self.list

    def append(self, widget):
        self.list_children.append(widget)
        widget.pack(fill = tk.X, expand = True)
    
    def insert(self, index, widget):
        index_cpy = index
        if index_cpy >= len(self.list_children):
            self.append(widget)
            return
        
        elif index_cpy < 0:
            self.insert(0, widget)
            return
        
        # forget items below
        for i in range(index, len(self.list_children)):
            self.chidlren[i].forget()
        
        # insert to list
        self.list_children.insert(index, widget)

        # repack items
        for i in range(index, len(self.list_children)):
            self.list_children[i].pack(fill = tk.X, expand = True)

    
    def remove(self, index):
        if index in self.list_children:
            self.list_children[index].forget()
        
        # update indexes
        while index < len(self.list_children) - 1:
            self.list_children[index] = self.list_children[index + 1]
            index += 1
        
        # delete highest index
        del self.list_children[len(self.list_children) - 1]
    
    def remove_widget(self, widget):
        widget.forget()
        self.list_children.remove(widget)