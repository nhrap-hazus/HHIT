# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 16:21:42 2020

@author: Colin Lindeman
"""


import tkinter as tk
from tkinter import ttk
from HURREVACmain import Hurrevac

myclass = Hurrevac()

#Get storm data
#Need to add handling if url is bad or its response is bad
myclass.getStormsResponse()
myclass.getYears()

stormYears = myclass.StormYears
stormYears.sort()
stormYears = tuple(stormYears)

#for windows 10 4k screens...
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass



root = tk.Tk()
root.geometry("600x700")
root.resizable(False,False)
root.title("Hurrevac Download and Export BETA")

#1
ttk.Label(root, text="Select a Basin", padding=(30,10)).pack()
ttk.Separator(root, orient="horizontal").pack(fill="x")

selected_stormBasin = tk.StringVar()
stormBasin = ttk.Combobox(root, textvariable=selected_stormBasin)
stormBasin['values'] = ('al','ep')
stormBasin.pack()
stormBasin['state'] = "readonly"
stormBasin.bind("<<ComboboxSelected>>")

#2
ttk.Separator(root, orient="horizontal").pack(fill="x")
ttk.Label(root, text="Select a Year", padding=(30,10)).pack()
                       
selected_stormYear = tk.StringVar()
stormYear = ttk.Combobox(root, textvariable=selected_stormYear)
stormYear['values'] = (stormYears)
stormYear.pack()
stormYear['state'] = "readonly"
def handle_selection(event):
    print("selected year is", selected_stormYear.get())
    print(stormYear.get())
stormYear.bind("<<ComboboxSelected>>", handle_selection)

#3
ttk.Separator(root, orient="horizontal").pack(fill="x")
ttk.Label(root, text="Select a Storm", padding=(30,10)).pack()

selected_stormName = tk.StringVar()
stormName = ttk.Combobox(root, textvariable=selected_stormName)
stormName['values'] = ()
stormName.pack()
stormName['state'] = "readonly"
def handle_stormNameSelection(event):
    print("selected storm name is", selected_stormName.get())
    print(stormName.get())
stormName.bind("<<ComboboxSelected>>", handle_stormNameSelection)

#4
ttk.Separator(root, orient="horizontal").pack(fill="x")
ttk.Label(root, text="Or Enter a StormId", padding=(30,10)).pack()

selected_stormId = tk.StringVar()
stormId = ttk.Entry(root, textvariable=selected_stormId)
stormId.pack()
#this needs validation that the entry conforms to the standards


#5

# ttk.Separator(root, orient="horizontal").pack(fill="x")
# ttk.Label(root, text="Export to JSON", padding=(30,10)).pack()
# exportToJSONFilePath_button = ttk.Button(root, text="Save As")
# exportToJSONFilePath_button.pack()

# exportToJSON_button = ttk.Button(root, text="Export")
# exportToJSON_button.pack()

#6
ttk.Separator(root, orient="horizontal").pack(fill="x")
ttk.Label(root, text="Export to Hazus (SQL Server)", padding=(30,10)).pack()
exportToHazusSqlServer = ttk.Button(root, text="Export")
exportToHazusSqlServer.pack()
ttk.Separator(root, orient="horizontal").pack(fill="x")

#7
quit_button = ttk.Button(root, text="Quit", command=root.destroy)
quit_button.pack(side="bottom")


root.mainloop()
