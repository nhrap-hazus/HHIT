# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 09:36:01 2020
Requirements: Python 3.7, Anaconda3 64bit
@author: Colin Lindeman
"""

import tkinter as tk
import tkinter.ttk as ttk
import pandas as pd
import numpy as np
import json
import math
from math import radians, cos, sin, asin, sqrt
import geopandas
from geopandas.tools import sjoin

try:
    with open("hurrevac_settings.json") as f:
        hurrevacSettings = json.load(f)
except:
    with open("./src/hurrevac_settings.json") as f:
        hurrevacSettings = json.load(f)
    
def popupmsg(msg):
    tk.messagebox.showinfo(message=msg)

def processStormJSON(inputJSON):
    try:
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
        
        '''Load variables from the settings file'''
        HurrevacRHurr34Factor = hurrevacSettings['HurrevacRHurr34Factor']
        HurrevacRHurr50Factor = hurrevacSettings['HurrevacRHurr50Factor']
        HurrevacRHurr64Factor = hurrevacSettings['HurrevacRHurr64Factor']
        HurrevacVmaxFactor = hurrevacSettings['HurrevacVmaxFactor']
        HurrevacKnotToMphFactor = hurrevacSettings['HurrevacKnottoMphFactor']
        jsonColumns = hurrevacSettings['jsonColumns']
        OptimizeStormTrack = hurrevacSettings['OptimizeStormTrack']
        
        '''Set to false to not perform any threshold checks on advisory or forecast points'''
        thresholdCheck = True
        
        '''Create dataframe for input when passing from hurrevac_main.py where it is stored as a dictionary from json...'''
        dfJSON = pd.DataFrame(inputJSON)
        # Filter the JSON by selecting which fields to keep...
        df = dfJSON[jsonColumns].copy()
        
        
        
        '''CALCULATE huStormTrack FIELDS for advisory (non-forecast) points...'''
        '''huStormTrackPtID'''
        #assigns a number sequentially starting from row 0. The rows should already be sorted by time asc
        startNumber = 1
        endNumber = len(df) + 1
        df.insert(0, 'huStormTrackPtID', range(startNumber, endNumber))
        #see also forecast section
        
        '''huScenarioName'''
        # Get the greatest dateTime row (last advisory)...
        maxAdvisory = df.loc[df['dateTime'].idxmax()]
        #Only get last advisories info to avoid issues with name changes and typoes (i.e. HARVEY, Harvey, TropicalDepression19)
        df['huScenarioName'] = maxAdvisory['stormName'] + "_Adv_" + maxAdvisory['number'] + "_" + maxAdvisory['stormId'][:2].upper() + maxAdvisory['stormId'][-4:]
    
        '''PointIndex'''
        df['PointIndex'] = np.nan
        
        '''TimeStep'''
        try:
            df['dateTime'] = pd.to_datetime(df['dateTime'], unit='ms')
            df['startDateTime'] = df['dateTime'].iloc[0] #get the first row's datatime value for new field
            df['TimeStep'] = df['dateTime'] - df['startDateTime']
            df['TimeStep'] = df['TimeStep'] / np.timedelta64(1,'h')
            df['TimeStep'] = df['TimeStep'].apply(np.int64)
        except Exception as e:
            print('TimeStep')
            print(e)
        
        '''Latitude'''
        df.rename(columns = {'centerLatitude':'Latitude'}, inplace=True)
    
        '''Longitude'''
        df.rename(columns = {'centerLongitude':'Longitude'}, inplace=True)
        
        '''bInland (intersect method)'''
        def createInlandList(inputDF):
            '''Requires TimeStep be populated; run before calc maxwindspeed.'''
            TimeStepList = []
            try:
                point = geopandas.GeoDataFrame(inputDF, geometry=geopandas.points_from_xy(inputDF.Longitude, inputDF.Latitude)).copy()
                point.crs = "epsg:4326"
                try:
                    polygonPath = './src/assets/spatial/cb_2018_us_nation_5m_EPSG4326.shp'
                    polygon = geopandas.GeoDataFrame.from_file(polygonPath)
                except Exception as e:
                    print('polygon issue')
                    print(polygonPath)
                    print(e)
                pointInPolys = sjoin(point, polygon, how='left')
                inlandPoints = pointInPolys[pointInPolys.index_right.notnull()].copy()
                inlandPointsDF = pd.DataFrame(inlandPoints.drop(columns='geometry'))
                TimeStepList = inlandPointsDF['TimeStep'].to_list()
            except Exception as e:
                print('inlandlist issue')
                print(e)
            return TimeStepList
        
        def InlandUpdate(row, inlandList):
            try:
                if row['TimeStep'] in inlandList:
                    return 1
                else:
                    return 0
            except Exception as e:
                print('inlandupdate issue')
                print(e)
                
        try:
            inlandList = createInlandList(df)
        except Exception as e:
            print('binlandlist issue')
            print(e)        
        try:
            df['bInland'] = df.apply(lambda row: InlandUpdate(row, inlandList), axis=1)
        except Exception as e:
            print('binland issue')
            print(e)
        #see also forecast section
        
        '''TranslationSpeed'''
        df['TranslationSpeed'] = 0
        #see also forecast section
        
        # '''TranslationSpeed'''
        #commented out as this can be calculated by Hazus
        # #read speed in nautical miles directly for advisory points
        # def translationSpeedCalc(row):
        #     speedKnots = row['speed']
        #     speedMph = speedKnots * HurrevacKnotToMphFactor
        #     return speedMph
        # df['TranslationSpeed'] = df.apply(lambda row: translationSpeedCalc(row), axis=1)
        # #see also forecast section
    
        '''RadiusToMaxWinds'''
        df['RadiusToMaxWinds'] = 0
        
        '''MaxWindSpeed'''
        def MaxWindSpeedCalc(row):
            '''input must be in nautical miles; bInland must be calculated beforehand.'''
            currentForecastDict = row['currentForecast']
            maxWinds = currentForecastDict['maxWinds']
            maxWindsMPH = maxWinds * HurrevacKnotToMphFactor
            maxWindsMPHHVF = maxWindsMPH * HurrevacVmaxFactor
            return maxWindsMPHHVF
        try:
            df['MaxWindSpeed'] = df.apply(lambda row: MaxWindSpeedCalc(row), axis=1)
        except Exception as e:
            print('MaxWindSpeed issue')
            print(e)
        
        '''RadiusToHurrWindsType''' 
        def radiusToHurrWindsTypeCalc(row):
            '''use maxwind*vmaxfactor in mph to determine'''
            MaxWindSpeedMPH = row['MaxWindSpeed']
            if MaxWindSpeedMPH <= 57:
                return "T"
            elif MaxWindSpeedMPH > 57 and MaxWindSpeedMPH < 74:
                return "5"
            elif MaxWindSpeedMPH >= 74:
                return "H"
            else:
                return np.nan
        try:
            df['RadiusToHurrWindsType'] = df.apply(lambda row: radiusToHurrWindsTypeCalc(row), axis=1)
        except Exception as e:
            print('RadiusToHurrWindsType issue')
            print(e)
        
        '''Central Presssure'''
        df.rename(columns = {'minimumPressure':'CentralPressure'}, inplace=True)
        #see also forecast section
        
        '''ProfileParameter'''
        #pass
            
        '''RadiusToXWinds (Max, regression)'''
        def RadiusToXWinds(WindFields, windCat, RHurrXFactor):
            '''input windspeed radii distance must be in nautical miles'''
            if len(WindFields['windFields']) > 0:
                windCats = []
                for x in WindFields['windFields']:
                    windCats.append(int(x['windSpeed']))
                if windCat in windCats:
                    for x in WindFields['windFields']:
                        if int(x['windSpeed']) == windCat:
                            radiiMax = max(x['extent']['northEast'], x['extent']['southEast'], x['extent']['northWest'], x['extent']['southWest'])
                            #Kept for reference just in case:
                            # if windCat in (34, 50):
                            #     regressionValue = 0.8996 * radiiMax - 0.5031
                            # elif windCat in (64):
                            #     regressionValue = 0.9472 * radiiMax - 0.277
                            # if regressionValue < 0:
                            #     regressionValue = 0
                            # value = (regressionValue * HurrevacKnotToMphFactor) * RHurrXFactor
                            value = (radiiMax * HurrevacKnotToMphFactor) * RHurrXFactor
                            return value
                else:
                    return 0.0
            else:
                return 0.0
                
        def AdvisoryPointRadiusToXWinds(row, windCat, RHurrXFactor):
            currentForecastDict = row['currentForecast']
            return RadiusToXWinds(currentForecastDict, windCat, RHurrXFactor)
        
        #Caculate all wind radii...
        try:
            df['RadiusTo34KWinds'] = df.apply(lambda row: AdvisoryPointRadiusToXWinds(row, 34, HurrevacRHurr34Factor), axis=1)
            df['RadiusTo50KWinds'] = df.apply(lambda row: AdvisoryPointRadiusToXWinds(row, 50, HurrevacRHurr50Factor), axis=1)
            df['RadiusToHurrWinds'] = df.apply(lambda row: AdvisoryPointRadiusToXWinds(row, 64, HurrevacRHurr64Factor), axis=1)
        except Exception as e:
            print('RadiusToXWinds')
            print(e)
    
        '''Zero out wind radii based on maxwindspeed...'''
        try:
            for i in range(0, len(df)):
                '''this requires that maxwindspeed is in mph and has hurrevac vmax factor applied'''
                CurrentMaxWindSpeed = df.loc[i, 'MaxWindSpeed']
                if CurrentMaxWindSpeed <= 57:
                    df.loc[i, 'RadiusTo50KWinds'] = 0
                    df.loc[i, 'RadiusToHurrWinds'] = 0
                elif CurrentMaxWindSpeed > 57 and CurrentMaxWindSpeed < 74:
                    df.loc[i, 'RadiusTo34KWinds'] = 0
                    df.loc[i, 'RadiusToHurrWinds'] = 0
                elif CurrentMaxWindSpeed >= 74:
                    df.loc[i, 'RadiusTo34KWinds'] = 0
                    df.loc[i, 'RadiusTo50KWinds'] = 0
                else:
                    pass
        except Exception as e:
            print('Wind Radii Cleanup')
            print(e)
    
        '''NewCentralPressure'''
        #pass
        
        '''NewTranslationSpeed'''
        #pass
        
        '''WindSpeedFactor'''
        #pass
        
        '''bForecast'''
        df['bForecast'] = 0
        #see also forecast section
        
        '''NewRadiusToHurrWinds'''
        #pass
        
        '''NewRadiusTo50KWinds'''
        #pass
        
        '''NewRadiusTo34KWinds'''
        #pass
        
        '''bInland MaxWindSpeed Adjustment'''
        '''First landfall point doesn't get adjusted'''
        try:
            previousInland = None
            for i in df.index:
                currentInland = df.loc[i, 'bInland']
                if i == 0:
                    '''First row won't have a previous'''
                    pass
                elif currentInland == 1 and previousInland == 1:
                    '''change all but the first row that has inland'''
                    df.loc[i, 'MaxWindSpeed'] = df.loc[i, 'MaxWindSpeed'] * 1.15
                else:
                    pass
                previousInland = currentInland
        except Exception as e:
            print('bInland MaxWindSpeed issue')
            print(e)



        '''FORECAST POINTS OF LAST ADVISORY, CALCULATE FIELDS...'''
        maxAdvisory = df.loc[df['dateTime'].idxmax()]
        dfForecasts = pd.json_normalize(maxAdvisory['futureForecasts'])
        if dfForecasts.size > 0:
            '''Forecast Rename the columns to match the main dataframe schema...'''
            dfForecasts.rename(columns = {'latitude':'Latitude',\
                                          'longitude':'Longitude',\
                                          'maxWinds':'MaxWindSpeed',\
                                          'hour':'dateTime'}, inplace=True)
            
            #Set forecast point values from last advisories values...
            dfForecasts['bForecast'] = 1
            dfForecasts['advisoryId'] = maxAdvisory['advisoryId']
            dfForecasts['stormName'] = maxAdvisory['stormName']
            dfForecasts['stormId'] = maxAdvisory['stormId']
            dfForecasts['huScenarioName'] = maxAdvisory['huScenarioName']
            dfForecasts['RadiusToMaxWinds'] = maxAdvisory['RadiusToMaxWinds']
            dfForecasts['number'] = maxAdvisory['number']
            
            '''Forecast huStormTrackPtID'''
            startNumber = int(maxAdvisory['huStormTrackPtID']) + 1
            endNumber = int(maxAdvisory['huStormTrackPtID']) + len(dfForecasts)+1
            dfForecasts.insert(0, 'huStormTrackPtID', range(startNumber, endNumber))
        
            '''Forecast timeStep'''
            dfForecasts['dateTime'] = dfForecasts['dateTime'].astype('datetime64[ms]')
            dfForecasts['startDateTime'] = maxAdvisory['startDateTime']
            try:
                dfForecasts['TimeStep'] = dfForecasts['dateTime'] - dfForecasts['startDateTime']
                dfForecasts['TimeStep'] = dfForecasts['TimeStep'] / np.timedelta64(1,'h')
                dfForecasts['TimeStep'] = dfForecasts['TimeStep'].apply(np.int64)
            except Exception as e:
                print('Forecast TimeStep')
                print(e)
            dfForecasts.drop(columns=['startDateTime'], inplace=True)
        
            # '''bInland Status method'''
            # dfForecasts['bInland'] = 0
            # def TESTforecastInland(row):
            #     try:
            #         status = row['status']
            #         if status:
            #             if 'inland' in status.lower():
            #                 return 1
            #             else:
            #                 return 0
            #         else:
            #             return 0
            #     except Exception as e:
            #         print('Exception: forecast inland')
            #         print(e)
            # try:
            #     dfForecasts['bInland'] = dfForecasts.apply(lambda row: TESTforecastInland(row), axis=1) 
            # except Exception as e:
            #     print('Forecast bInland')
            #     print(e)
            
            '''Forecast bInland (intersect method)'''
            dfForecasts['bInland'] = 0
            try:
                forecastInlandList = createInlandList(dfForecasts)
            except Exception as e:
                print('Forecast binlandlist issue')
                print(e)
            try:
                dfForecasts['bInland'] = dfForecasts.apply(lambda row: InlandUpdate(row, forecastInlandList), axis=1)
            except Exception as e:
                print('Forecast binland issue')
                print(e)        
        
            '''Forecast MaxWindSpeed'''
            def MaxWindSpeedForecastCalc(row):
                maxWinds = row['MaxWindSpeed']
                maxWindsMPH = maxWinds * HurrevacKnotToMphFactor
                maxWindsMPHHVF = maxWindsMPH * HurrevacVmaxFactor
                return maxWindsMPHHVF
            try:
                dfForecasts['MaxWindSpeed'] = df.apply(lambda row: MaxWindSpeedCalc(row), axis=1)
            except Exception as e:
                print('Forecast MaxWindSpeed')
                print(e)
        
            '''Forecast RadiusToHurrWindsType'''
            try:
                dfForecasts['RadiusToHurrWindsType'] = dfForecasts.apply(lambda row: radiusToHurrWindsTypeCalc(row), axis=1)
            except Exception as e:
                print('Forecast radiustohurrwindstype')
                print(e)
                
            '''Forecast bInland MaxWindSpeed Adjustment'''
            try:
                previousInland = None
                for i in dfForecasts.index:
                    currentInland = dfForecasts.loc[i, 'bInland']
                    if i == 0:
                        '''First row won't have a previous'''
                        pass
                    elif currentInland == 1 and previousInland == 1:
                        '''change all but the first row that has inland'''
                        dfForecasts.loc[i, 'MaxWindSpeed'] = dfForecasts.loc[i, 'MaxWindSpeed'] * 1.15
                    else:
                        pass
                    previousInland = currentInland
            except Exception as e:
                print('Forecast bInland MaxWindSpeed issue')
                print(e)
        
            '''Forecast RadiusToXWinds'''
            dfForecasts['RadiusTo34KWinds'] = dfForecasts.apply(lambda row: RadiusToXWinds(row, 34, HurrevacRHurr34Factor), axis=1)
            dfForecasts['RadiusTo50KWinds'] = dfForecasts.apply(lambda row: RadiusToXWinds(row, 50, HurrevacRHurr50Factor), axis=1)
            dfForecasts['RadiusToHurrWinds'] = dfForecasts.apply(lambda row: RadiusToXWinds(row, 64, HurrevacRHurr64Factor), axis=1)
        
            '''Zero out wind radii based on maxwindspeed...'''
            try:
                for i in range(0, len(dfForecasts)):
                    '''this requires that maxwindspeed is in mph and has hurrevac vmax factor applied'''
                    CurrentMaxWindSpeed = dfForecasts.loc[i, 'MaxWindSpeed']
                    if CurrentMaxWindSpeed <= 57:
                        dfForecasts.loc[i, 'RadiusTo50KWinds'] = 0
                        dfForecasts.loc[i, 'RadiusToHurrWinds'] = 0
                    elif CurrentMaxWindSpeed > 57 and CurrentMaxWindSpeed < 74:
                        dfForecasts.loc[i, 'RadiusTo34KWinds'] = 0
                        dfForecasts.loc[i, 'RadiusToHurrWinds'] = 0
                    elif CurrentMaxWindSpeed >= 74:
                        dfForecasts.loc[i, 'RadiusTo34KWinds'] = 0
                        dfForecasts.loc[i, 'RadiusTo50KWinds'] = 0
                    else:
                        pass
            except Exception as e:
                print('Forecast Wind Radii Cleanup')
                print(e)
        
            '''Forecast Translation Speed'''
            dfForecasts['TranslationSpeed'] = 0
            
            # '''Translation Speed'''
            # #speed in mph from advisory point to forecast point 0, etc...
            # dfForecasts['distance'] = np.nan
            # dfForecasts['TranslationSpeed'] = np.nan
            # #set default point...
            # latA = maxAdvisory['Latitude']
            # longA = maxAdvisory['Longitude']
            # for i in range(0, len(dfForecasts)):
            #     latB = dfForecasts.loc[i, 'Latitude']
            #     longB = dfForecasts.loc[i, 'Longitude']
            #     distanceMiles = distance(latA, latB, longA, longB)
            #     dfForecasts.loc[i, 'distance'] = distanceMiles
            #     #set beginning point to previous forecast point for next loop...
            #     latA = latB
            #     longA = longB
            # timeA = maxAdvisory['TimeStep']
            # for i in range(0, len(dfForecasts)):
            #     timeB = dfForecasts.loc[i, 'TimeStep']
            #     timeHours = timeB - timeA
            #     distanceMiles = dfForecasts.loc[i, 'distance']
            #     speedMPH = distanceMiles / timeHours
            #     dfForecasts.loc[i, 'TranslationSpeed'] = speedMPH
            #     #set beginning point to previous forecast point for next loop...
            #     timeA = timeB
            
            '''Forecast direction'''
            dfForecasts['direction'] = np.nan
            try:
                #set default point...
                latA = maxAdvisory['Latitude']
                longA = maxAdvisory['Longitude']
                for i in range(0, len(dfForecasts)):
                    latB = dfForecasts.loc[i, 'Latitude']
                    longB = dfForecasts.loc[i, 'Longitude']
                    #create point tuple...
                    pointA = (float(latA), float(longA))
                    pointB = (float(latB), float(longB))
                    compassBearing = calculate_initial_compass_bearing(pointA, pointB)
                    dfForecasts.loc[i, 'direction'] = compassBearing
                    #set beginning point to previous forecast point for next loop...
                    latA = latB
                    longA = longB
            except Exception as e:
                print('Forecast Direction:')
                print(e)
            
            '''Forecast CentralPressure'''
            pressureBar = 1013.0
            dfForecasts['CentralPressure'] = np.nan
            try:
                #set default point...
                cpA = maxAdvisory['CentralPressure']
                mwsA = maxAdvisory['MaxWindSpeed']
                for i in range(0, len(dfForecasts)):
                    mwsB = dfForecasts.loc[i, 'MaxWindSpeed']
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
            except Exception as e:
                print('Forecast centralPressure:')
                print(e)
                
            
            
            '''CLEANUP THE FORECASTS DATAFRAME TO APPEND TO THE MAIN DATAFRAME...'''
            '''Format the forecasts before appending...'''
            dfForecasts = dfForecasts[['number',\
                                       'huStormTrackPtID',\
                                        'huScenarioName',\
                                        'TimeStep',\
                                        'Latitude',\
                                        'Longitude',\
                                        'TranslationSpeed',\
                                        'RadiusToMaxWinds',\
                                        'MaxWindSpeed',\
                                        'CentralPressure',\
                                        'RadiusToHurrWinds',\
                                        'RadiusTo50KWinds',\
                                        'RadiusTo34KWinds',\
                                        'bInland',\
                                        'bForecast',\
                                        'RadiusToHurrWindsType',\
                                        'advisoryId',\
                                        'stormName',\
                                        'stormId',\
                                        'dateTime']]
            dfForecasts = dfForecasts.sort_values(by='dateTime', ascending=True)
        
            '''APPEND forecast records to main dataframe...'''
            df = df.append(dfForecasts, ignore_index=True)
            
            
            
        '''THRESHOLD CHECKS AND DATA CONDITIONING...'''        
        if thresholdCheck:
            '''If lat,long is 0,0; delete the row'''
            df = df.loc[(df['Latitude'] != 0) & (df['Longitude'] != 0)]            
            
            '''Only for interim (i.e. 4A), Where ever there is a 0 or null, use previous'''
            for fieldName in ['RadiusToHurrWinds',\
                              'RadiusTo50KWinds',\
                              'RadiusTo34KWinds']:
                previous = None
                for i in df.index:
                    current = df.loc[i, fieldName]
                    numberValue = str(df.loc[i, 'number'])
                    if i == 0:
                        '''First row won't have a previous'''
                        pass
                    else:
                        if 'A' in numberValue.upper():
                            if current == 0:
                                df.loc[i, fieldName] = previous
                            else:
                                pass
                        else:
                            pass
                    previous = current
                    
            '''For all'''
            '''MaxWindSpeed'''
            def ThresholdMaxWindSpeed(row):
                '''this requires that maxwindspeed is in mph and has hurrevac vmax factor applied'''
                MaxWindSpeedValue = row['MaxWindSpeed']
                if MaxWindSpeedValue < 40:
                    return 40
                else:
                    return MaxWindSpeedValue
            try:
                df['MaxWindSpeed'] = df.apply(lambda row: ThresholdMaxWindSpeed(row), axis=1)
            except Exception as e:
                print('Threhold Check MaxWindSpeed')
                print(e)

            '''RadiusTo34KWinds'''
            def ThresholdRadiusTo34KWinds(row):
                if row['MaxWindSpeed'] < 58 and row['RadiusTo34KWinds'] == 0:
                    return 30
                else:
                    return row['RadiusTo34KWinds']
            try:
                df['RadiusTo34KWinds'] = df.apply(lambda row: ThresholdRadiusTo34KWinds(row), axis=1)
            except Exception as e:
                print('Threhold Check RadiusTo34KWinds')
                print(e)
        


        '''TRIM and FORMAT the dataframe to match the HAZUS tables...'''
        df_huStormTrack = df[['huStormTrackPtID',\
                        'huScenarioName',\
                        'PointIndex',\
                        'TimeStep',\
                        'Latitude',\
                        'Longitude',\
                        'TranslationSpeed',\
                        'RadiusToMaxWinds',\
                        'MaxWindSpeed',\
                        'CentralPressure',\
                        'RadiusToHurrWinds',\
                        'RadiusTo50KWinds',\
                        'RadiusTo34KWinds',\
                        'bInland',\
                        'bForecast',\
                        'RadiusToHurrWindsType']].copy()
            
        def optimizeTrack(df):
            '''Drop all but two rows from the head and tail each where the maxwindspeed is the minimum value(or below)'''
            try:
                '''HEAD'''
                dfRange = df.index
                headRowCount = 0
                for i in dfRange:  
                    if df.loc[i, 'MaxWindSpeed'] <= 40:
                        headRowCount += 1
                    else:
                        break
                if headRowCount > 2:
                    headRows = headRowCount - 2
                    df.drop(df.head(headRows).index, inplace=True)
                '''TAIL'''
                dfRangeReversed = reversed(df.index)
                tailRowCount = 0
                for i in dfRangeReversed:  
                    if df.loc[i, 'MaxWindSpeed'] <= 40:
                        tailRowCount += 1
                    else:
                        break
                if tailRowCount > 2:
                    tailRows = tailRowCount - 2
                    df.drop(df.tail(tailRows).index, inplace=True)
                '''huStormTrackPtID'''
                #assigns a number sequentially starting from row 0. The rows should already be sorted by time asc
                df.drop(columns=['huStormTrackPtID'], inplace=True)
                startNumber = 1
                endNumber = len(df) + 1
                df.insert(0, 'huStormTrackPtID', range(startNumber, endNumber))
            except Exception as e:
                print('optimizeTrack', e)
        
        if OptimizeStormTrack == 1:
            try:
                optimizeTrack(df_huStormTrack)
            except Exception as e:
                print('Optimize Track', e)
            
            
        '''CREATE huScenario TABLE...'''
        df_huScenarioName = df['huScenarioName']
        df_huScenario = df_huScenarioName.drop_duplicates().to_frame() #Not sure if this is the best method to get a list of one...
        df_huScenario['bSSCurrent'] = 0
        df_huScenario['bTimeStep'] = 0
        df_huScenario['bTranslationSpeed'] = 0
        df_huScenario['bMaxWindSpeed'] = 1
        df_huScenario['bCentralPressure'] = 1
        df_huScenario['bProfileParameter'] = 0
        df_huScenario['bRadiusType'] = 0
        df_huScenario['Info'] = "HURREVAC HVX Storm Advisory Download;" + maxAdvisory['stormName'] + " " + maxAdvisory['stormId']
        df_huScenario['Type'] = 4
        
        
        
        '''RETURN THE THREE OBJECTS...'''
        huScenarioName = df_huScenario['huScenarioName'].unique().tolist()[0]
        huStormTrack = df_huStormTrack
        huScenario = df_huScenario
        return huScenarioName, huScenario, huStormTrack
    
    except Exception as e:
        print(e)
        popupmsg('Error processing Storm JSON.')
    
            
#Test some of the code above...
if __name__ == "__main__":
    popupmsg('popupmsg test one two.')