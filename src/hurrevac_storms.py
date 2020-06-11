# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 09:36:01 2020
Requirements: Python 3.7, Anaconda3 64bit
@author: Colin Lindeman
"""

import tkinter as tk
import tkinter.ttk as ttk
import urllib.request
import json
import hurrevac_storm

try:
    with open("hurrevac_settings.json") as f:
        hurrevacSettings = json.load(f)
except:
    with open("./src/hurrevac_settings.json") as f:
        hurrevacSettings = json.load(f)

def popupmsg(msg):
    NORM_FONT= ("Tahoma", 12)
    popup = tk.Toplevel()
    popup.wm_title("!")
    # Gets the requested values of the height and width.
    windowWidth = popup.winfo_reqwidth()
    windowHeight = popup.winfo_reqheight()
    # Gets both half the screen width/height and window width/height
    positionRight = int(popup.winfo_screenwidth()/2 - windowWidth/2)
    positionDown = int(popup.winfo_screenheight()/3 - windowHeight/2)
    # Positions the window in the center of the page.
    popup.geometry("+{}+{}".format(positionRight, positionDown))
    label = ttk.Label(popup, text=msg, font=NORM_FONT)
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    popup.mainloop()

def get_key(val, my_dict): 
    for key, value in my_dict.items(): 
         if val == value: 
             return key 
    return "key doesn't exist"

class StormsInfo:
    def __init__(self):
        ''' '''
        self.GetStormsJSON()
        self.GetStormsTypes()
        self.GetStormsYears()
        self.GetStormsBasins()
    
    def GetStormsJSON(self):
        openUrl = urllib.request.urlopen(hurrevacSettings['HurrevacStormsURL'])
        
        if(openUrl.getcode()==200):
            stormsdata = openUrl.read()
            stormsJSON = json.loads(stormsdata)
            self.JSON = stormsJSON
        else:
            print("Error receiving data", openUrl.getcode())
            
    def GetStormsTypes(self):
        #working with json
        StormTypes = hurrevacSettings['ShowStormTypes']
        StormTypesList = []
        for key in StormTypes.keys():
            if StormTypes[key]:
                StormTypesList.append(key)
        StormTypesList.sort()
        self.types = tuple(StormTypesList)

    def GetStormsBasins(self):
        #working with json
        StormBasins = hurrevacSettings['BasinsDictionary']
        StormBasinsLabels = list(StormBasins.values())
        self.basins = tuple(StormBasinsLabels)

    def GetStormsYears(self):
        #working with json
        yearList = []
        for i in self.JSON:
            try:
                year = int(i)
            except:
                year = i
            yearList.append(year)
        yearList.sort(reverse=True)
        self.years = tuple(yearList)
        
    # def GetOptimizeStormTrack(self):
    #     with open("hurrevac_settings.json") as f:
    #         hurrevacSettings = json.load(f)
    #     self.optimizeStormTrack = hurrevacSettings['OptimizeStormTrack']
    
    def GetStormNames(self, stormTypes, basinLabel, year):
        '''Get basins code from label in settings.json'''
        '''It would be nice to sort storms by alphabet then greek alphabet 
           when there are more than 26 storms'''
        StormBasins = hurrevacSettings['BasinsDictionary']
        basinCode = get_key(basinLabel, StormBasins)
        #working with json
        stormNameStatusIDList = []
        activeStorms = []
        historicStorms = []
        exerciseStorms = []
        simulatedStorms = []
        '''Iterate over storms for a given year, append to each list'''
        try:
            year = str(year)
        except:
            year = year
        for storm in self.JSON[year]:
            stormName = str(storm['name'])
            stormId = str(storm['stormId'])
            stormStatus = str(storm['status'])
            stormBasin = str(storm['basin'])
            stormLabel = stormName + " (" + stormStatus + ") " + " [" + stormId + "]"
            if stormBasin == basinCode:
                if stormStatus == "Simulated":
                    simulatedStorms.append(stormLabel)
                elif stormStatus == "Historical":
                    historicStorms.append(stormLabel)
                elif stormStatus == "Exercise":
                    exerciseStorms.append(stormLabel)
                elif stormStatus == "Active":
                    activeStorms.append(stormLabel)
        activeStorms.sort()
        historicStorms.sort()
        exerciseStorms.sort()
        simulatedStorms.sort()
        '''Determine which type of storms are added to the main list'''
        if 'Active' in stormTypes:
            for i in activeStorms:
                stormNameStatusIDList.append(i)
        if 'Historical' in stormTypes:
            for i in historicStorms:
                stormNameStatusIDList.append(i)
        if 'Exercise' in stormTypes:
            for i in exerciseStorms:
                stormNameStatusIDList.append(i)
        if 'Simulated' in stormTypes:
            for i in simulatedStorms:
                stormNameStatusIDList.append(i)
        if len(stormNameStatusIDList) > 0:
            return tuple(stormNameStatusIDList)
        else:
            return ('No Storms Found',)

class StormInfo:
    def GetStormJSON(self, StormId):
        self.Id = StormId
        #from internet
        #attribute and used as input to GetStormDataframe
        url = hurrevacSettings['HurrevacStormURL'] + "/" + StormId
        openUrl = urllib.request.urlopen(url)
        if(openUrl.getcode()==200):
            #Need to check if response is 200 but there is no data "[]", ie a non-valid stormid request.
            stormdata = openUrl.read()
            stormJSON = json.loads(stormdata)
            self.JSON = stormJSON
        else:
            popupmsg("Error receiving data. Check settings.json url or site is down or changed.")
            print("Error receiving data", openUrl.getcode())

    def GetStormDataframe(self, stormJSON):
        #from other python script
        #attribute and used as input to ExportToJSON
        stormDataframes = hurrevac_storm.processStormJSON(stormJSON)
        self.huScenarioName = stormDataframes[0]
        self.huScenario = stormDataframes[1]
        self.huStormTrack = stormDataframes[2]

#Test some of the code above...
if __name__ == "__main__":
    myclass = StormsInfo()
    # myclass.GetStormsJSON()
    # myclass.GetStormsBasins()
    # myclass.GetStormsYears()
    
    print("all possible types from config:", myclass.types)
    print()
    print("all possible basins from config:", myclass.basins)
    print()
    print("all possible years from source:", myclass.years)
    print()
    print("Atlantic 2014 storm labels:", myclass.GetStormLabels('Atlantic', '2014'))
    print()
    print("Eastern Pacific 2020 storm labels:", myclass.GetStormLabels('Eastern Pacific', '2020'))
    print()
    print("Atlantic 2014 storm names:", myclass.GetStormNames(['Active', 'Historical', 'Exercise', 'Simulated'], 'Atlantic', '2014'))
    print()
    print("Eastern Pacific 2020 storm names:", myclass.GetStormNames(['Active', 'Historical', 'Exercise', 'Simulated'], 'Eastern Pacific', '2020'))
    print()

    
    storm1 = StormInfo()
    storm1.GetStormJSON("al012020")
    #print(storm1.Id)
    #print(storm1.JSON)
    print(storm1.Id)
    storm1.GetStormDataframe(storm1.JSON)
    print(storm1.huScenario)
    print(storm1.huStormTrack)
    
