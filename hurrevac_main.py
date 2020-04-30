# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 09:36:01 2020
Requirements: Python 3.7, Anaconda3 64bit
@author: Colin Lindeman
"""

import pandas as pd
import numpy as np
import urllib
import json
import statistics
import math
from math import radians, cos, sin, asin, sqrt 
import pyodbc
from sqlalchemy import create_engine
import hurrevac_process_json

def get_key(val, my_dict): 
    for key, value in my_dict.items(): 
         if val == value: 
             return key 
    return "key doesn't exist"

class StormsInfo:
    def GetStormsJSON(self):
        with open(r".\hurrevac_settings.json") as f:
            hurrevacSettings = json.load(f)
        openUrl = urllib.request.urlopen(hurrevacSettings['HurrevacStormsURL'])
        
        if(openUrl.getcode()==200):
            stormsdata = openUrl.read()
            stormsJSON = json.loads(stormsdata)
            self.JSON = stormsJSON
        else:
            print("Error receiving data", openUrl.getcode())

    def GetStormsBasins(self):
        #working with json
        # this is needed to filter storm ids for user
        with open(r".\hurrevac_settings.json") as f:
            hurrevacSettings = json.load(f)
        StormBasins = hurrevacSettings['BasinsDictionary']
        StormBasinsLabels = list(StormBasins.values())
        StormBasinsLabels.sort()
        self.basins = tuple(StormBasinsLabels)

    def GetStormsYears(self):
        # this is needed to filter storm ids for user
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
    
    def GetStormLabels(self, basinLabel, year):
        with open(r".\hurrevac_settings.json") as f:
            hurrevacSettings = json.load(f)
        StormBasins = hurrevacSettings['BasinsDictionary']
        basin = get_key(basinLabel, StormBasins)
        #working with json
        stormNameIdStatusList = []
        try:
            year = str(year)
        except:
            year = year
        for storm in self.JSON[year]:
            stormName = str(storm['name'])
            stormId = str(storm['stormId'])
            stormStatus = str(storm['status'])
            stormBasin = str(storm['basin'])
            # stormDict = {'stormName':stormName, \
            #              'stormId':stormId, \
            #              'stormStatus':stormStatus}
            # stormNameIdStatusList.append(stormDict)
            stormLabel = stormName + " (" + stormStatus + ") " + " [" + stormId + "]"
            if stormBasin == basin and stormStatus != "Simulated":
                stormNameIdStatusList.append(stormLabel)
            stormNameIdStatusList.sort()
        return tuple(stormNameIdStatusList)

class StormInfo:
    def GetStormJSON(self, StormId):
        self.Id = StormId
        #from internet
        #attribute and used as input to GetStormDataframe
        with open(r".\hurrevac_settings.json") as f:
            hurrevacSettings = json.load(f)
        url = hurrevacSettings['HurrevacStormURL'] + "/" + StormId
        openUrl = urllib.request.urlopen(url)
        if(openUrl.getcode()==200):
            stormdata = openUrl.read()
            stormJSON = json.loads(stormdata)
            self.JSON = stormJSON
        else:
            print("Error receiving data", openUrl.getcode())

    def GetStormDataframe(self, stormJSON):
        #from other python script
        #attribute and used as input to ExportToJSON
        stormDataframes = hurrevac_process_json.processStormJSON(stormJSON)
        self.huScenarioName = stormDataframes[0]
        self.huScenario = stormDataframes[1]
        self.huStormTrack = stormDataframes[2]

#Tools to export data
def ExportToJSON(inputDataFrame, outputPath):
    df = inputDataFrame
    df.to_json(outputPath)

def CheckScenarioName(huScenarioName):
    with open(r".\hurrevac_settings.json") as f:
        hurrevacSettings = json.load(f)
    server = hurrevacSettings['HazusServerName']
    userName = hurrevacSettings['HazusUserName']
    password = hurrevacSettings['HazusPassword']
    engine = create_engine('mssql+pyodbc://'+userName+':'+password+'@'+server+'/syHazus?driver=SQL+Server')
    conn = engine.connect()
    scenariosDF = pd.read_sql_table(table_name="huScenario", con=conn)
    scenariosList = scenariosDF['huScenarioName'].values.tolist()
    if huScenarioName not in scenariosList:
        return True
    else:
        return False

def ExportToHazus(huScenarioName, huScenario, huStormTrack):
    with open(r".\hurrevac_settings.json") as f:
        hurrevacSettings = json.load(f)
    server = hurrevacSettings['HazusServerName']
    userName = hurrevacSettings['HazusUserName']
    password = hurrevacSettings['HazusPassword']
    engine = create_engine('mssql+pyodbc://'+userName+':'+password+'@'+server+'/syHazus?driver=SQL+Server')
    conn = engine.connect()
    huScenarioDoesntExist = CheckScenarioName(huScenarioName)
    if huScenarioDoesntExist:
        huScenario.to_sql(name="huScenario", con=conn, if_exists='append', index=False)
        huStormTrack.to_sql(name="huStormTrack", con=conn, if_exists='append', index=False)
        return "scenario does not exist, proceed"
    else:
        #inform user that scenarioname already exists and how to resolve it, popup window
        return "either scenario already exists or to_sql failed"
    
#Test some of the code above...
if __name__ == "__main__":
    myclass = StormsInfo()
    myclass.GetStormsJSON()
    myclass.GetStormsBasins()
    myclass.GetStormsYears()
    
    print("all possible basins from config:", myclass.basins)
    print()
    print("all possible years from source:", myclass.years)
    print()
    print("Atlantic 2014 storms:", myclass.GetStormLabels('Atlantic', '2014'))
    print()
    print("Eastern Pacific 2020 storms:", myclass.GetStormLabels('Eastern Pacific', '2020'))
    print()
    
    storm1 = StormInfo()
    storm1.GetStormJSON("al032016")
    print(storm1.Id)
    #print(storm1.JSON)
    print(storm1.Id)
    storm1.GetStormDataframe(storm1.JSON)
    print(storm1.huScenario)
    print(storm1.huStormTrack)
    
    print(CheckScenarioName("HARVEY_2017_stm_2204PM"))
    print(CheckScenarioName("HARVEY - Adv 53 AL2018"))
    #print(ExportToHazus(storm1.huScenarioName, storm1.huScenario, storm1.huStormTrack))
    ExportToHazus(storm1.Id, storm1.huScenario, storm1.huStormTrack)
    
    