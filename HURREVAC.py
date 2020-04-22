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

class Hurrevac:
    def getResponse(self):
        with open(r".\hurrevacSettings.json") as f:
            hurrevacSettings = json.load(f)
        operUrl = urllib.request.urlopen(hurrevacSettings['HurrevacStormsURL'])
        if(operUrl.getcode()==200):
            data = operUrl.read()
            jsonData = json.loads(data)
        else:
            print("Error receiving data", operUrl.getcode())
        self.StormsJSON = jsonData
        return jsonData
    
    def getYears(self):
        yearList = []
        for i in self.StormsJSON:
            #Try to convert the year from string to an integer...
            try:
                year = int(i)
            except:
                year = i
            yearList.append(year)
        self.StormYears = yearList
        return yearList
    
    def getStormIds(self, year):
        stormIdList = []
        try:
            year = str(year)
        except:
            year = year
        for i in self.StormsJSON[year]:
            stormIdList.append(i["stormId"])
        self.StormIds = stormIdList
        return stormIdList
    
    #This needs work
    def getStormList(self):
        stormsDict = []
        #only get id, name, basin, status...
        stormsDF =pd.read_json(self.StormsJSON)
        for year in self.StormYears:
            for storm in stormsDF[str(year)]:
                stormYear = int(year)
                stormId = storm['stormId']
                stormName = storm['name']
                stormType = storm['type']
                maxWinds = storm['maxWinds']
                stormStatus = storm['status']
                basin = storm['basin']
                startDate = storm['startDate']
                endDate = storm['endDate']
                stormDict = {'stormYear':stormYear, \
                             'stormId':stormId, \
                             'stormName':stormName, \
                             'stormType':stormType, \
                             'maxWinds':maxWinds, \
                             'stormStatus':stormStatus, \
                             'basin':basin, \
                             'startDate':startDate, \
                             'endDate':endDate}
                stormsDict.append(stormDict)
        dfStorms = pd.DataFrame(stormsDict)
        StormList = dfStorms.sort_values(by=['stormYear'])
        self.StormList = StormList
        return StormList

    def getStormBasins(self):
        with open(r".\hurrevacSettings.json") as f:
            hurrevacSettings = json.load(f)
        StormBasins = hurrevacSettings['Basins']
        self.StormBasins = StormBasins
        return StormBasins
        

    def downloadStormJSON(self, stormid):
        #
        pass
    
    def processStormJSON(self, inputPath):
        #Get settings from ./hurrevacSettings.json...
        with open(r".\hurrevacSettings.json") as f:
            hurrevacSettings = json.load(f)
        HurrevacRHurr50Factor = hurrevacSettings['HurrevacRHurr50Factor']
        HurrevacRHurr64Factor = hurrevacSettings['HurrevacRHurr64Factor']
        HurrevacVmaxFactor = hurrevacSettings['HurrevacVmaxFactor']
        HurrevacKnotToMphFactor = hurrevacSettings['HurrevacKnottoMphFactor']
        jsonColumns = hurrevacSettings['jsonColumns']
        
        #Create dataframe for input json...
        dfJSON = pd.read_json(inputPath)
        # Filter the JSON by selecting which fields to keep...
        df = dfJSON[jsonColumns].copy()
        
        
        #CALCULATE huStormTrack FIELDS...
        #huStormTrackPtID
        # df['PointIndex'] = df['number']
        # df.rename(columns = 'PointIndex':'number', inplace=True)
        
        #huScenarioName
        # get the greatest dateTime row...
        maxAdvisory = df.loc[df['dateTime'].idxmax()]
        df['huScenarioName'] = df['stormId'].str[:2] + df['stormName'] + "_" + maxAdvisory['number']
        
        #PointIndex
        df['PointIndex'] = None
        
        #TimeStep
        df['startDateTime'] = df.loc[df['number'] == '1', 'dateTime'].iloc[0]
        df['timeStep'] = df['dateTime'] - df['startDateTime']
        df['timeStep'] = df['timeStep'] / np.timedelta64(1,'h')
        df['timeStep'] = df['timeStep'].apply(np.int64)
        df.drop(columns=['startDateTime'], inplace=True)
        
        #Latitude
        #df['Latitude'] = df['centerLatitude']
        #df.rename(columns = 'centerLatitude':'Latitude', inplace=True)

        #Longitude
        # df['Longitude'] = df['centerLongitude']
        # df.rename(columns = 'centerLongitude':'Longitude', inplace=True)
        
        #TranslationSpeed
    
        #RadiusToMaxWinds
        
        #MaxWindSpeed
        def maxGusts(row):
            currentForecastDict = row['currentForecast']
            maxGusts = currentForecastDict['maxGusts']
            #convert from knots to mph...
            maxGustsMPH = maxGusts * HurrevacKnotToMphFactor
            #reduce by HurrevacVmaxFactor...
            maxGustsMPHHVF = maxGustsMPH * HurrevacVmaxFactor
            return maxGustsMPHHVF
        df['MaxWindSpeed'] = df.apply(lambda row: maxGusts(row), axis=1)
        
        #Central Presssure
        
        #ProfileParameter
        
        #RadiusToXWinds
        # average of north, south, east, west extent from currentForecast
        def radiusTo34Winds(row):
            currentForecastDict = row['currentForecast']
            windFields = currentForecastDict['windFields']
            radiiList = []
            if len(windFields) > 0:
                for field in windFields:
                    if field['windSpeed']==34:
                        northEast34 = field['extent']['northEast']
                        southEast34 = field['extent']['southEast']
                        southWest34 = field['extent']['southWest']
                        northWest34 = field['extent']['northWest']
                        radiiList.append(northEast34)
                        radiiList.append(southEast34)
                        radiiList.append(southWest34)
                        radiiList.append(northWest34)
                    else:
                        radiiList.append(0)
            else:
                radiiList.append(0)
            radiiAverage = statistics.mean(radiiList)
            #convert to mph, apply hurreac value here
            return radiiAverage
        
        def radiusTo50Winds(row):
            currentForecastDict = row['currentForecast']
            windFields = currentForecastDict['windFields']
            radiiList = []
            if len(windFields) > 0:
                for field in windFields:
                    if field['windSpeed']==50:
                        northEast50 = field['extent']['northEast']
                        southEast50 = field['extent']['southEast']
                        southWest50 = field['extent']['southWest']
                        northWest50 = field['extent']['northWest']
                        radiiList.append(northEast50)
                        radiiList.append(southEast50)
                        radiiList.append(southWest50)
                        radiiList.append(northWest50)
                    else:
                        radiiList.append(0)
            else:
                radiiList.append(0)
            radiiAverage = statistics.mean(radiiList)
            #convert to mph, apply hurreac value here
            return radiiAverage
        
        def radiusTo64Winds(row):
            currentForecastDict = row['currentForecast']
            windFields = currentForecastDict['windFields']
            radiiList = []
            if len(windFields) > 0:
                for field in windFields:
                    if field['windSpeed']==64:
                        northEast64 = field['extent']['northEast']
                        southEast64 = field['extent']['southEast']
                        southWest64 = field['extent']['southWest']
                        northWest64 = field['extent']['northWest']
                        radiiList.append(northEast64)
                        radiiList.append(southEast64)
                        radiiList.append(southWest64)
                        radiiList.append(northWest64)
                    else:
                        radiiList.append(0)
            else:
                radiiList.append(0)
            radiiAverage = statistics.mean(radiiList)
            #convert to mph, apply hurreac value here
            return radiiAverage
        
        df['RadiusTo34KWinds'] = df.apply(lambda row: radiusTo34Winds(row), axis=1)
        df['RadiusTo50KWinds'] = df.apply(lambda row: radiusTo50Winds(row), axis=1)
        df['RadiusToHurrWinds'] = df.apply(lambda row: radiusTo64Winds(row), axis=1)
    
        #NewCentralPressure
        
        #NewTranslationSpeed
        
        #WindSpeedFactor
        
        #bInland
        
        #bForecast
        
        #RadiusToHurrWindsType
        
        #NewRadiusToHurrWinds
        
        #NewRadiusTo50KWinds
        
        #NewRadiusTo34KWinds
        
        #Process last advisories forecast points...
        maxAdvisory = df.loc[df['dateTime'].idxmax()]
        dfForecasts = pd.json_normalize(maxAdvisory['futureForecasts'])
        dfForecasts['bForecast'] = 1
        dfForecasts['advisoryId'] = maxAdvisory['advisoryId']
        dfForecasts['stormName'] = maxAdvisory['stormName']
        dfForecasts['stormId'] = maxAdvisory['stormId']
        dfForecasts['huScenarioName'] = maxAdvisory['huScenarioName']
        
        startNumber = int(maxAdvisory['number']) + 1
        endNumber = int(maxAdvisory['number']) + len(dfForecasts)+1
        dfForecasts.insert(0, 'number', range(startNumber, endNumber))
    
        #Calculate speed in mph? knots? from advisory point to forecast point 0, etc...
        dfForecasts['speed'] = None
        
        #Calculate timeStep
        #dfForecasts['DateTime'] = pd.to_datetime(df['dateTime'], unit='s')
        dfForecasts['hour'] = dfForecasts['hour'].astype('datetime64[ms]')
        dfForecasts['startDateTime'] = df.loc[df['number'] == '1', 'dateTime'].iloc[0]
        dfForecasts['timeStep'] = dfForecasts['hour'] - dfForecasts['startDateTime']
        dfForecasts['timeStep'] = dfForecasts['timeStep'] / np.timedelta64(1,'h')
        dfForecasts['timeStep'] = dfForecasts['timeStep'].apply(np.int64)
        dfForecasts.drop(columns=['startDateTime'], inplace=True)
        
        #Calculate minimum pressure
        def forecastMinimumPressure(row):
            pressureBar = 1013.0
            cpi = maxAdvisory['minimumPressure'] 
            mwsi = maxAdvisory['MaxWindSpeed']
            mwsf = row['MaxWindSpeed']
            #this formula needs testing/approval from Doug
            cpf = (pressureBar - (pressureBar - cpi) * (mwsf/mwsi)**2)
            cpf = int(cpf + 0.5)
            return cpf
        dfForecasts['minimumPressure'] = df.apply(lambda row: forecastMinimumPressure(row), axis=1)
        
        #Rename the columns to match the main dataframe schema...
        dfForecasts.rename(columns = {'latitude':'centerLatitude',\
                                      'longitude':'centerLongitude',\
                                      'maxGusts':'MaxWindSpeed',\
                                      'hour':'dateTime'}, inplace=True)
        dfForecasts = dfForecasts[['advisoryId',\
                                   'stormName',\
                                    'stormId',\
                                    'huScenarioName',\
                                    'number',\
                                    'bForecast',\
                                    'dateTime',\
                                    'timeStep',\
                                    'centerLatitude','centerLongitude',\
                                    'MaxWindSpeed',
                                    'minimumPressure']]
        dfForecasts = dfForecasts.sort_values(by='dateTime', ascending=True)
        df = df.append(dfForecasts, ignore_index=True)
        
        #Check field value thresholds and set values if broken
        
        #Trim and Format the dataframe to match the HAZUS tables...
        
        self.stormData = df
        
    def exportToJSON(self, outputPath):
        df = self.stormData
        df.to_json(outputPath)
            
    def exportToHazus(self):
        pass
    
#Test some of the code above...
if __name__ == "__main__":
    myclass = Hurrevac()
    myclass.processStormJSON(r"C:\Projects\HURREVAC_HVX_JSON_20200300\Data\ep092014.json")
    myclass.exportToJSON(r"C:\Projects\HURREVAC_HVX_JSON_20200300\Data\testOutput.json")
    myclass.getResponse()
    print(myclass.getYears())
    print(myclass.getStormIds(2020))
