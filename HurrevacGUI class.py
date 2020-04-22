# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 16:21:42 2020

@author: Colin Lindeman
"""


import tkinter as tk
from tkinter import ttk
from HURREVAC import Hurrevac


#for windows 10 4k screens...
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass
        
class Application(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        
        self.master.geometry(width=512, height=256)
        self.master.config() #what does this do?
        self.master.resizable(False,False)
        
        
        self.master.title("Hurrevac Download and Export BETA")
        
        self.myclass = Hurrevac()
        
        #Get storm data
        #Need to add handling if url is bad or its response is bad
        self.myclass.getResponse()
        
        self.stormYears = self.myclass.getYears()
        self.stormYears.sort()
        self.stormYears = tuple(self.stormYears)

        #1
        self.ttk.Label(root, text="Select a Basin", padding=(30,10)).pack()
        self.ttk.Separator(root, orient="horizontal").pack(fill="x")
        
        self.selected_stormBasin = tk.StringVar()
        self.stormBasin = ttk.Combobox(root, textvariable=self.selected_stormBasin)
        self.stormBasin['values'] = ('al','ep')
        self.stormBasin.pack()
        self.stormBasin['state'] = "readonly"

        
        #2
        self.ttk.Separator(root, orient="horizontal").pack(fill="x")
        self.ttk.Label(root, text="Select a Year", padding=(30,10)).pack()
                               
        self.selected_stormYear = tk.StringVar()
        self.stormYear = ttk.Combobox(root, textvariable=self.selected_stormYear)
        self.stormYear['values'] = (self.stormYears)
        self.stormYear.pack()
        self.stormYear['state'] = "readonly"
        
        #3
        self.ttk.Separator(root, orient="horizontal").pack(fill="x")
        self.ttk.Label(root, text="Select a Storm", padding=(30,10)).pack()
        
        self.selected_stormName = tk.StringVar()
        self.stormName = ttk.Combobox(root, textvariable=self.selected_stormName)
        self.stormName['values'] = ()
        self.stormName.pack()
        self.stormName['state'] = "readonly"

        
        #4
        self.ttk.Separator(root, orient="horizontal").pack(fill="x")
        self.ttk.Label(root, text="Export to JSON", padding=(30,10)).pack()
        self.exportToJSONFilePath_button = ttk.Button(root, text="Save As")
        self.exportToJSONFilePath_button.pack()
        
        self.exportToJSON_button = ttk.Button(root, text="Export")
        self.exportToJSON_button.pack()
        
        #5
        self.ttk.Separator(root, orient="horizontal").pack(fill="x")
        self.ttk.Label(root, text="Export to Hazus (SQL Server)", padding=(30,10)).pack()
        self.exportToHazusSqlServer = ttk.Button(root, text="Export")
        self.exportToHazusSqlServer.pack()
        self.ttk.Separator(root, orient="horizontal").pack(fill="x")
        
        #6
        self.quit_button = ttk.Button(root, text="Quit", command=root.destroy)
        self.quit_button.pack(side="bottom")
        
    def load_StormNames(self, *args):
        stormBasinSelection = self.stormBasin.selection_get()
        stormYearSelection = self.stormYear.selection_get()
    
        self.data = self.getStormIds(stormYearSelection)
    
        # clear the stormName listbox
        self.stormName.delete(0, tk.END)
    
        # insert the stormNames into the stormNames listbox
        for i in (self.data):
            self.stormName.insert(i)

root = tkinter.tk()
app = Application(root) 
app.mainloop()
