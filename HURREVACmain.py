# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 09:36:01 2020
Requirements: Python 3.7, Anaconda3 64bit
@author: Colin Lindeman
"""

import pandas as pd
import urllib
import json

class Hurrevac:
    def getStormsResponse(self):
        # this is to get the json storm data from the source
        with open(r".\hurrevacSettings.json") as f:
            hurrevacSettings = json.load(f)
        openUrl = urllib.request.urlopen(hurrevacSettings['HurrevacStormsURL'])
        if(openUrl.getcode()==200):
            stormsdata = openUrl.read()
            stormsJSON = json.loads(stormsdata)
        else:
            print("Error receiving data", openUrl.getcode())
        self.StormsJSON = stormsJSON

    def getStormResponse(self, stormid):
        # this is to get the json storm data from the source
        with open(r".\hurrevacSettings.json") as f:
            hurrevacSettings = json.load(f)
        url = hurrevacSettings['HurrevacStormURL'] + "/" + stormid
        openUrl = urllib.request.urlopen(url)
        if(openUrl.getcode()==200):
            stormDF = pd.read_json(url)
        else:
            print("Error receiving data", openUrl.getcode())
        return stormDF

    def getStormBasins(self):
        #working with json
        # this is needed to filter storm ids for user
        with open(r".\hurrevacSettings.json") as f:
            hurrevacSettings = json.load(f)
        StormBasins = hurrevacSettings['Basins']
        self.StormBasins = StormBasins

    def getYears(self):
        # this is needed to filter storm ids for user
        #working with json
        yearList = []
        for i in self.StormsJSON:
            try:
                year = int(i)
            except:
                year = i
            yearList.append(year)
        self.StormYears = yearList
    
    def getStormIds(self, year):
        #working with json
        stormIdList = []
        try:
            year = str(year)
        except:
            year = year
        for i in self.StormsJSON[year]:
            stormIdList.append(i["stormId"])
        return stormIdList
    
    def getStormNamesByBasinYear(self, basin, year):
        #working with json
        stormNameIdStatusList = []
        try:
            year = str(year)
        except:
            year = year
        for storm in self.StormsJSON[year]:
            stormName = str(storm['name'])
            #stormId = str(storm['stormId'])
            stormStatus = str(storm['status'])
            # stormDict = {'stormName':stormName, \
            #              'stormId':stormId, \
            #              'stormStatus':stormStatus}
            # stormNameIdStatusList.append(stormDict)
            stormLabel = stormName + " (" + stormStatus + ")"
            stormNameIdStatusList.append(stormLabel)
        return stormNameIdStatusList        
        
    def exportToJSON(self, outputPath):
        df = self.stormData
        df.to_json(outputPath)
            
    def exportToHazus(self):
        pass
    
#Test some of the code above...
if __name__ == "__main__":
    myclass = Hurrevac()
    myclass.getStormsResponse()
    myclass.getStormBasins()
    myclass.getYears()
    
    print("all possible basins from config:", myclass.StormBasins)
    print()
    print("all possible years from source:", myclass.StormYears)
    print()
    print("Atlatic 2014 storms:", myclass.getStormNamesByBasinYear('al', '2014'))
    print()
    print("Eastern Pacific 2020 storms:", myclass.getStormNamesByBasinYear('ep', '2020'))
    print()
    x = myclass.getStormResponse("si062020")
    print("Stormid si062020 pandas dataframe", x.head(5))
    #myclass.processStormJSON(r"C:\Projects\HURREVAC_HVX_JSON_20200300\Data\ep092014.json")
    #myclass.exportToJSON(r"C:\Projects\HURREVAC_HVX_JSON_20200300\Data\testOutput.json")