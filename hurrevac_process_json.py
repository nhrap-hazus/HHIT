# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 09:36:01 2020
Requirements: Python 3.7, Anaconda3 64bit
@author: Colin Lindeman
"""

import pandas as pd
import numpy as np
import json
import statistics
import math
from math import radians, cos, sin, asin, sqrt 


def processStormJSON(inputPath):
    def distance(lat1, lat2, lon1, lon2): 
        # The math module contains a function named 
        # radians which converts from degrees to radians. 
        lon1 = radians(lon1) 
        lon2 = radians(lon2) 
        lat1 = radians(lat1) 
        lat2 = radians(lat2) 
        # Haversine formula  
        dlon = lon2 - lon1  
        dlat = lat2 - lat1 
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * asin(sqrt(a))  
        # Radius of earth in 6371 kilometers. Use 3956 for miles 
        r = 3956
        # calculate the result 
        return(c * r) 
    
    def calculate_initial_compass_bearing(pointA, pointB):
        """
        https://gist.github.com/jeromer/2005586
        Calculates the bearing between two points.
        The formulae used is the following:
            θ = atan2(sin(Δlong).cos(lat2),
                      cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
        :Parameters:
          - `pointA: The tuple representing the latitude/longitude for the
            first point. Latitude and longitude must be in decimal degrees
          - `pointB: The tuple representing the latitude/longitude for the
            second point. Latitude and longitude must be in decimal degrees
        :Returns:
          The bearing in degrees
        :Returns Type:
          float
        """
        if (type(pointA) != tuple) or (type(pointB) != tuple):
            raise TypeError("Only tuples are supported as arguments")
        lat1 = math.radians(pointA[0])
        lat2 = math.radians(pointB[0])
        diffLong = math.radians(pointB[1] - pointA[1])
        x = math.sin(diffLong) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
                * math.cos(lat2) * math.cos(diffLong))
        initial_bearing = math.atan2(x, y)
        # Now we have the initial bearing but math.atan2 return values
        # from -180° to + 180° which is not what we want for a compass bearing
        # The solution is to normalize the initial bearing as shown below
        initial_bearing = math.degrees(initial_bearing)
        compass_bearing = (initial_bearing + 360) % 360
        return compass_bearing
    
    #working with json
    with open(r".\hurrevac_settings.json") as f:
        hurrevacSettings = json.load(f)
    HurrevacRHurr50Factor = hurrevacSettings['HurrevacRHurr50Factor']
    HurrevacRHurr64Factor = hurrevacSettings['HurrevacRHurr64Factor']
    HurrevacVmaxFactor = hurrevacSettings['HurrevacVmaxFactor']
    HurrevacKnotToMphFactor = hurrevacSettings['HurrevacKnottoMphFactor']
    ValidWindSpeedMPHThresholdGreaterThanMin = hurrevacSettings['ValidWindSpeedMPHThresholdGreaterThanMin']
    ValidWindSpeedMPHThresholdLessThanMax = hurrevacSettings['ValidWindSpeedMPHThresholdLessThanMax']
    ValidCentralPressuremBarThresholdGreaterThanMin = hurrevacSettings['ValidCentralPressuremBarThresholdGreaterThanMin']
    ValidCentralPressuremBarThresholdLessThanMax = hurrevacSettings['ValidCentralPressuremBarThresholdLessThanMax']
    jsonColumns = hurrevacSettings['jsonColumns']
    
    #Create dataframe for input json when importing from .json file...
    #dfJSON = pd.read_json(inputPath)
    #Create dataframe for input when passing from hurrevac_main.py where it is stored as a dictionary from json...
    dfJSON = pd.DataFrame(inputPath)
    # Filter the JSON by selecting which fields to keep...
    df = dfJSON[jsonColumns].copy()
    
    
    #CALCULATE huStormTrack FIELDS...

    #huStormTrackPtID
    #assigns a number sequentially starting from row 0. The rows should already be sorted by time asc
    startNumber = 1
    endNumber = len(df) + 1
    df.insert(0, 'huStormTrackPtID', range(startNumber, endNumber))
    #see also forecast section
    
    #huScenarioName
    # Get the greatest dateTime row (last advisory)...
    maxAdvisory = df.loc[df['dateTime'].idxmax()]
    #Only get last advisories info to avoid issues with name changes and typoes (i.e. HARVEY, Harvey, TropicalDepression19)
    df['huScenarioName'] = maxAdvisory['stormName'] + "_Adv_" + maxAdvisory['number'] + "_" + maxAdvisory['stormId'][:2].upper() + maxAdvisory['stormId'][-4:]

    
    #PointIndex
    df['PointIndex'] = np.nan
    
    #TimeStep
    df['dateTime'] = pd.to_datetime(df['dateTime'], unit='ms')
    df['startDateTime'] = df.loc[df['number'] == '1', 'dateTime'].iloc[0]
    df['TimeStep'] = df['dateTime'] - df['startDateTime']
    df['TimeStep'] = df['TimeStep'] / np.timedelta64(1,'h')
    df['TimeStep'] = df['TimeStep'].apply(np.int64)
    df.drop(columns=['startDateTime'], inplace=True)
    
    #Latitude
    df.rename(columns = {'centerLatitude':'Latitude'}, inplace=True)

    #Longitude
    df.rename(columns = {'centerLongitude':'Longitude'}, inplace=True)
    
    #TranslationSpeed
    #read speed in nautical miles directly for advisory points
    def translationSpeed(row):
        speedKnots = row['speed']
        speedMph = speedKnots * HurrevacKnotToMphFactor
        return speedMph
    df['TranslationSpeed'] = df.apply(lambda row: translationSpeed(row), axis=1)
    #see also forecast section

    #RadiusToMaxWinds
    
    #MaxWindSpeed
    def MaxWindSpeed(row):
        currentForecastDict = row['currentForecast']
        maxWinds = currentForecastDict['maxWinds']
        #convert from knots to mph...
        maxWindsMPH = maxWinds * HurrevacKnotToMphFactor
        #reduce by HurrevacVmaxFactor...
        maxWindsMPHHVF = maxWindsMPH * HurrevacVmaxFactor
        return maxWindsMPHHVF
    df['MaxWindSpeed'] = df.apply(lambda row: MaxWindSpeed(row), axis=1)
    
    #Central Presssure
    df.rename(columns = {'minimumPressure':'CentralPressure'}, inplace=True)
    #see also forecast section
    
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
        #convert to mph
        radiiAverageMph = (radiiAverage * HurrevacKnotToMphFactor)
        return radiiAverageMph
    
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
        #convert to mph, apply hurreac value
        radiiAverageMph = (radiiAverage * HurrevacKnotToMphFactor) * HurrevacRHurr50Factor
        return radiiAverageMph
    
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
        #convert to mph, apply hurreac value
        radiiAverageMph = (radiiAverage * HurrevacKnotToMphFactor) * HurrevacRHurr64Factor
        return radiiAverageMph
    
    df['RadiusTo34KWinds'] = df.apply(lambda row: radiusTo34Winds(row), axis=1)
    df['RadiusTo50KWinds'] = df.apply(lambda row: radiusTo50Winds(row), axis=1)
    df['RadiusToHurrWinds'] = df.apply(lambda row: radiusTo64Winds(row), axis=1)

    #NewCentralPressure
    
    #NewTranslationSpeed
    
    #WindSpeedFactor
    
    #bInland
    df['bInland'] = 0
    #see also forecast section
    
    #bForecast
    df['bForecast'] = 0
    #see also forecast section
    
    #RadiusToHurrWindsType
    def radiusToHurrWindsType(row):
        if row['RadiusToHurrWinds'] > 0:
            return "H"
        elif row['RadiusTo50KWinds'] > 0:
            return "5"
        elif row['RadiusTo34KWinds'] > 0:
            return "T"
        else:
            return np.nan
    df['RadiusToHurrWindsType'] = df.apply(lambda row: radiusToHurrWindsType(row), axis=1)
    
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
    
    #huStormTrackPtID
    startNumber = int(maxAdvisory['huStormTrackPtID']) + 1
    endNumber = int(maxAdvisory['huStormTrackPtID']) + len(dfForecasts)+1
    dfForecasts.insert(0, 'huStormTrackPtID', range(startNumber, endNumber))

    #timeStep
    dfForecasts['hour'] = dfForecasts['hour'].astype('datetime64[ms]')
    dfForecasts['startDateTime'] = df.loc[df['number'] == '1', 'dateTime'].iloc[0]
    dfForecasts['TimeStep'] = dfForecasts['hour'] - dfForecasts['startDateTime']
    dfForecasts['TimeStep'] = dfForecasts['TimeStep'] / np.timedelta64(1,'h')
    dfForecasts['TimeStep'] = dfForecasts['TimeStep'].apply(np.int64)
    dfForecasts.drop(columns=['startDateTime'], inplace=True)

    #speed in mph? knots? from advisory point to forecast point 0, etc...
    dfForecasts['distance'] = np.nan
    dfForecasts['TranslationSpeed'] = np.nan
    #set default point...
    latA = maxAdvisory['Latitude']
    longA = maxAdvisory['Longitude']
    for i in range(0, len(dfForecasts)):
        latB = dfForecasts.loc[i, 'latitude']
        longB = dfForecasts.loc[i, 'longitude']
        distanceMiles = distance(latA, latB, longA, longB)
        dfForecasts.loc[i, 'distance'] = distanceMiles
        #set beginning point to previous forecast point for next loop...
        latA = latB
        longA = longB
    timeA = maxAdvisory['TimeStep']
    for i in range(0, len(dfForecasts)):
        timeB = dfForecasts.loc[i, 'TimeStep']
        timeHours = timeB - timeA
        distanceMiles = dfForecasts.loc[i, 'distance']
        speedMPH = distanceMiles / timeHours
        dfForecasts.loc[i, 'TranslationSpeed'] = speedMPH
        #set beginning point to previous forecast point for next loop...
        timeA = timeB
    
    #direction
    dfForecasts['direction'] = np.nan
    #set default point...
    latA = maxAdvisory['Latitude']
    longA = maxAdvisory['Longitude']
    for i in range(0, len(dfForecasts)):
        latB = dfForecasts.loc[i, 'latitude']
        longB = dfForecasts.loc[i, 'longitude']
        #create point tuple...
        pointA = (float(latA), float(longA))
        pointB = (float(latB), float(longB))
        compassBearing = calculate_initial_compass_bearing(pointA, pointB)
        dfForecasts.loc[i, 'direction'] = compassBearing
        #set beginning point to previous forecast point for next loop...
        latA = latB
        longA = longB
    
    #CentralPressure
    pressureBar = 1013.0
    dfForecasts['CentralPressure'] = np.nan
    #set default point...
    cpA = maxAdvisory['CentralPressure']
    mwsA = maxAdvisory['MaxWindSpeed']
    for i in range(0, len(dfForecasts)):
        mwsB = dfForecasts.loc[i, 'maxWinds']
        if mwsA <= 0:
            #this needs to be reworked to not stop if initial mwsA is 0!
            pass
        else:
            cpB = (pressureBar - (pressureBar - cpA) * (mwsB/mwsA)**2)
            cpB = int(cpB + 0.5)
            dfForecasts.loc[i, 'CentralPressure'] = cpB
            #set beginning point to previous forecast point for next loop...
            cpA = cpB
            mwsA = mwsB
    
    #bInland
    def TESTforecastInland(row):
        #placeholder until issue of row['status'] fails
        status = 0
        return status
    dfForecasts['bInland'] = df.apply(lambda row: TESTforecastInland(row), axis=1) 
    
    #Rename the columns to match the main dataframe schema...
    dfForecasts.rename(columns = {'latitude':'Latitude',\
                                  'longitude':'Longitude',\
                                  'maxGusts':'MaxWindSpeed',\
                                  'hour':'dateTime'}, inplace=True)
        
    #Format the forecasts before appending...
    dfForecasts = dfForecasts[['advisoryId',\
                       'stormName',\
                       'stormId',\
                       'huScenarioName',\
                       'huStormTrackPtID',\
                       'bForecast',\
                       'dateTime',\
                       'TimeStep',\
                       'Latitude',\
                       'Longitude',\
                       'TranslationSpeed',\
                       'MaxWindSpeed', \
                       'CentralPressure',\
                       'bInland']]
    dfForecasts = dfForecasts.sort_values(by='dateTime', ascending=True)
    
    #Append forecast records to main dataframe...
    df = df.append(dfForecasts, ignore_index=True)
    
    #Check field value thresholds and set values if broken
    df.loc[df['CentralPressure'] > ValidCentralPressuremBarThresholdLessThanMax, 'CentralPressure'] = ValidCentralPressuremBarThresholdLessThanMax
    df.loc[df['CentralPressure'] < ValidCentralPressuremBarThresholdGreaterThanMin, 'CentralPressure'] = ValidCentralPressuremBarThresholdGreaterThanMin
    
    #if MaxWindSpeed is 0, use previous advisories value
    MaxWindSpeedA = ValidWindSpeedMPHThresholdGreaterThanMin
    for i in range(0, len(df)):
        MaxWindSpeedB = df.loc[i, 'MaxWindSpeed']
        if df.loc[i, 'MaxWindSpeed'] == 0:
            df.loc[i, 'MaxWindSpeed'] = MaxWindSpeedA
        #set beginning point to previous forecast point for next loop...
        MaxWindSpeedA = MaxWindSpeedB
        
    df.loc[df['MaxWindSpeed'] > ValidWindSpeedMPHThresholdLessThanMax, "MaxWindSpeed"] = ValidWindSpeedMPHThresholdLessThanMax
    df.loc[df['MaxWindSpeed'] < ValidWindSpeedMPHThresholdGreaterThanMin, "MaxWindSpeed"] = ValidWindSpeedMPHThresholdGreaterThanMin
    
    #Trim and Format the dataframe to match the HAZUS tables...
    df_huStormTrack = df[['huStormTrackPtID',\
                    'huScenarioName',\
                    'PointIndex',\
                    'TimeStep',\
                    'Latitude',\
                    'Longitude',\
                    'TranslationSpeed',\
                    'MaxWindSpeed',\
                    'CentralPressure',\
                    'RadiusToHurrWinds',\
                    'RadiusTo50KWinds',\
                    'RadiusTo34KWinds',\
                    'bInland',\
                    'bForecast',\
                    'RadiusToHurrWindsType']]
        
    #Create huScenario table...
    df_huScenarioName = df['huScenarioName']
    #Not sure if this is the best method
    df_huScenario = df_huScenarioName.drop_duplicates().to_frame()
    
    df_huScenario['bSSCurrent'] = 1
    df_huScenario['bTimeStep'] = 0
    df_huScenario['bTranslationSpeed'] = 0
    df_huScenario['bMaxWindSpeed'] = 1
    df_huScenario['bCentralPressure'] = 1
    df_huScenario['bProfileParameter'] = 0
    df_huScenario['bRadiusType'] = 0
    df_huScenario['Info'] = "HURREVAC HVX Storm Advisory Download;" + maxAdvisory['stormName'] + " " + maxAdvisory['stormId']
    df_huScenario['Type'] = 4
        
    huScenarioName = df_huScenario['huScenarioName'].unique().tolist()[0]
    huStormTrack = df_huStormTrack
    huScenario = df_huScenario
    return huScenarioName, huScenario, huStormTrack
    
            
#Test some of the code above...
# if __name__ == "__main__":
#     myclass = Hurrevac()