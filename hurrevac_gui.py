# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 13:01:01 2020

@author: Colin Lindeman
"""
#for windows 10 4k screens...
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

from tkinter import *
import tkinter.ttk
import hurrevac_main
import re

#setup storms data
storms = hurrevac_main.StormsInfo()
storms.GetStormsJSON()
storms.GetStormsBasins()
stormBasins = tuple(storms.basins)
storms.GetStormsYears()
stormYears = tuple(storms.years)

class Application(Frame):

    def __init__(self, master=None, Frame=None):
        Frame.__init__(self, master)
        super(Application,self).__init__()
        self.grid(column = 1,row = 15,padx = 50,pady = 50)
        self.createWidgets()

    def getUpdateStormName(self, event):
        self.NameCombo['values'] = storms.GetStormLabels(self.BasinCombo.get(), self.YearCombo.get())
        
    def getUpdateStormId(self, event):
        #parse out the stormId from the stormLabel
        StormId = re.findall(".+\[(.+)\]", self.NameCombo.get())
        self.selected_stormId.set(StormId[0])
        
    def exportHazus(self):
        self.storm = hurrevac_main.StormInfo()
        self.storm.GetStormJSON(self.selected_stormId.get())
        self.storm.GetStormDataframe(self.storm.JSON)
        hurrevac_main.ExportToHazus(self.storm.huScenarioName, self.storm.huScenario, self.storm.huStormTrack)
        #launch success and next steps window to validate
        #launch failure (scenario already exists) and steps to resolve
        print('exportHazus',self.storm.huScenarioName)
        
    def exportJSON(self):
        self.storm = hurrevac_main.StormInfo()
        self.storm.GetStormJSON(self.selected_stormId.get())
        hurrevac_main.ExportToJSON(self.storm.huStormTrack, "C:/temp/"+self.selected_stormId.get()+".json")
        #launch success and window of locatoin of saved json file
        #launch failure
        print('exportJSON', self.selected_stormId.get())
        
    def createWidgets(self):
        Label(text = 'Basin:').grid(row = 2,column = 1,padx = 10)
        Label(text = 'Year:').grid(row = 4,column = 1,padx = 10)
        Label(text = 'Storm:').grid(row = 6,column = 1,padx = 10)
        Label(text = 'Storm Id:').grid(row = 8,column = 1,padx = 10)
        
        self.selected_stormId = tkinter.StringVar()
        self.IdEntry = tkinter.ttk.Entry(width = 10, justify='center', textvariable=self.selected_stormId)
        self.IdEntry.grid(row = 9,column = 1,pady = 10,padx = 10)
        
        self.NameCombo = tkinter.ttk.Combobox(width = 40, state="readonly")
        self.NameCombo.bind('<<ComboboxSelected>>', self.getUpdateStormId)
        self.NameCombo.grid(row = 7,column = 1,pady = 10,padx = 10)

        self.YearCombo = tkinter.ttk.Combobox(width = 6, justify='center', values = stormYears, state="readonly")
        self.YearCombo.bind('<<ComboboxSelected>>', self.getUpdateStormName)
        self.YearCombo.grid(row = 5,column = 1,padx = 10,pady = 10)
        
        self.BasinCombo = tkinter.ttk.Combobox(width = 15, values = stormBasins, state="readonly")
        self.BasinCombo.bind('<<ComboboxSelected>>', self.getUpdateStormName)
        self.BasinCombo.grid(row = 3,column = 1,padx = 10,pady = 10)

        self.hazusButton = tkinter.ttk.Button(text="Load to Hazus", command=self.exportHazus)
        self.hazusButton.grid(row = 10,column = 1,padx = 10,pady = 10)
        
        self.jsonButton = tkinter.ttk.Button(text="Export to JSON", command=self.exportJSON)
        self.jsonButton.grid(row = 11,column = 1,padx = 10,pady = 10)
        
        self.quitButton = tkinter.ttk.Button(text="Quit", command=self.master.destroy)
        self.quitButton.grid(row = 15,column = 1,padx = 10,pady = 10)

app = Application()
app.master.title('HurrEvac HVX ETL')
app.mainloop()

