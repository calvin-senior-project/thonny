import difflib
import tkinter as tk

from thonny import get_workbench
from thonny.tktextext import TweakableText
from thonny.plugins.codelive.utils import publish_delete, publish_insert

def patched_insert(text_widget, index, chars, *args):
    wb = get_workbench()
    TweakableText.insert(text_widget, index, chars, *args)
    publish_insert(wb, text_widget, text_widget.index(tk.INSERT), index, chars)

def patched_delete(text_widget, index1, index2 = None):
    wb = get_workbench()
    TweakableText.delete(text_widget, index1, index2)
    publish_delete(wb, text_widget, text_widget.index(tk.INSERT), index1, index2)

# def patched_perform_smart_backspace(text, event):
#     WB = get_workbench()

#     text._log_keypress_for_undo(event)

#     first, last = text.get_selection_indices()
#     if first and last:
#         text.delete(first, last)
#         text.mark_set("insert", first)
#         publish_delete(WB, text, first, last)
#         return "break"
#     # Delete whitespace left, until hitting a real char or closest
#     # preceding virtual tab stop.
#     chars = text.get("insert linestart", "insert")
#     if chars == "":
#         if text.compare("insert", ">", "1.0"):
#             # easy: delete preceding newline
#             insert_index = text.index("insert - 1c")
#             text.delete("insert-1c")
#             publish_delete(WB, text, insert_index)
#         else:
#             text.bell()  # at start of buffer
#         return "break"

#     if (chars.strip() != ""
#     ):  # there are non-whitespace chars somewhere to the left of the cursor
#         # easy: delete preceding real char
#         insert_index = text.index("insert - 1c")
#         text.delete("insert-1c")
#         publish_delete(WB, text, insert_index)
#         text._log_keypress_for_undo(event)
#         return "break"

#     # Ick.  It may require *inserting* spaces if we back up over a
#     # tab character!  This is written to be clear, not fast.
#     have = len(chars.expandtabs(text.tabwidth))
#     assert have > 0
#     want = ((have - 1) // text.indent_width) * text.indent_width
#     # Debug prompt is multilined....
#     # if text.context_use_ps1:
#     #    last_line_of_prompt = sys.ps1.split('\n')[-1]
#     # else:
#     last_line_of_prompt = ""
#     ncharsdeleted = 0
#     while 1:
#         if chars == last_line_of_prompt:
#             break
#         chars = chars[:-1]
#         ncharsdeleted = ncharsdeleted + 1
#         have = len(chars.expandtabs(text.tabwidth))
#         if have <= want or chars[-1] not in " \t":
#             break
    
#     first = text.index("insert-%dc" % ncharsdeleted)
#     last = text.index("insert")
    
#     text.delete(first, last)
#     publish_delete(WB, text, first, last)
    
#     if have < want:
#         publish_insert(WB,
#                        text,
#                        text.index("insert"),
#                        " " * (want - have))
#         text.insert("insert", " " * (want - have))

#     return "break"

# def patched_perform_return(text, event):
#     WB = get_workbench()
#     publish_insert(WB,
#                    text,
#                    text.index("insert"),
#                    "\n")
#     text.insert("insert", "\n")
    
#     return "break"

# def patched_change_indentation(text, increase):
#     wb = get_workbench()
#     head, tail, chars, lines = text._get_region()

#     # Text widget plays tricks if selection ends on last line
#     # and content doesn't end with empty line,
#     text_last_line = index2line(text.index("end-1c"))
#     sel_last_line = index2line(tail)
#     if sel_last_line >= text_last_line:
#         while not text.get(head, "end").endswith("\n\n"):
#             text.insert("end", "\n")
#             #broadcast inserts
#             #              )

#     for pos in range(len(lines)):
#         line = lines[pos]
#         if line:
#             raw, effective = classifyws(line, text.tabwidth)
#             if increase:
#                 effective = effective + text.indent_width
#             else:
#                 effective = max(effective - text.indent_width, 0)
#             lines[pos] = text._make_blanks(effective) + line[raw:]
#     text._set_region(head, tail, chars, lines, publish_change = True)
    
#     # Broadcast
#     return "break"

# def patched_perform_midline_tab(text, event):
#     pass

# def patched_perform_smart_tab(text, event):
#     pass

# def patched_set_region(text, head, tail, chars, lines, publish_change = False):
#     wb = get_workbench()
    
#     newchars = "\n".join(lines)
#     if newchars == chars:
#         text.bell()
#         return
#     text.tag_remove("sel", "1.0", "end")
#     text.mark_set("insert", head)
    
#     if publish_change:
#         publish_delete(wb, text, head, tail)
#     text.delete(head, tail)
    
#     text.insert(head, newchars)
#     if publish_change:
#         publish_insert(wb, text, head, newchars)
    
#     text.tag_add("sel", head, "insert")

#     return
