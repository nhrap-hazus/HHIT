# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 09:36:01 2020
Requirements: Python 3.7, Anaconda3 64bit
@author: Colin Lindeman
"""

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox as messagebox
import pandas as pd
import json
from sqlalchemy import create_engine

try:
    with open("hurrevac_settings.json") as f:
        hurrevacSettings = json.load(f)
except:
    with open("./src/hurrevac_settings.json") as f:
        hurrevacSettings = json.load(f)

def popupmsg(msg):
    tk.messagebox.showinfo(message=msg)

def popupmsgNextSteps(msg):
    NORM_FONT= ("Tahoma", 12)
    popup = tk.Toplevel()
    popup.grab_set()
    popup.wm_title("!")
    popup.resizable(0,0)
    # Gets the requested values of the height and width.
    windowWidth = popup.winfo_reqwidth()
    windowHeight = popup.winfo_reqheight()
    # Gets both half the screen width/height and window width/height
    positionRight = int(popup.winfo_screenwidth()/2 - windowWidth/2)
    positionDown = int(popup.winfo_screenheight()/3 - windowHeight/2)
    # Positions the window in the center of the page.
    popup.geometry("+{}+{}".format(positionRight, positionDown))
    
    label = ttk.Label(popup, text=msg, font=NORM_FONT)
    label.grid(row=1,column=0,padx=10,pady=10)
    try:
        #global img_NextSteps
        img_NextSteps = tk.PhotoImage(file="./src/assets/images/NextSteps.png")
        imageLabel = tk.Label(popup, image=img_NextSteps)
        imageLabel.image = img_NextSteps
        imageLabel.grid(row=2,column=0,padx=10,pady=10)
    except Exception as e:
        print(e)
    
    B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
    B1.grid(row=3,column=0,padx=10,pady=20)
    popup.mainloop()

def get_key(val, my_dict): 
    '''Currently not used'''
    for key, value in my_dict.items(): 
         if val == value: 
             return key 
    return "key doesn't exist"

#Tools to export data
def ExportToJSON(inputDataFrame, outputPath):
    df = inputDataFrame
    df.to_json(outputPath)

def CheckScenarioName(huScenarioName):
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
        popupmsg(f'Scenario "{huScenarioName}" already exists.\nPlease use "Hazus Hurricane Scenario Wizard" to edit or delete.')
        return False

def ExportToHazus(huScenarioName, huScenario, huStormTrack):
    server = hurrevacSettings['HazusServerName']
    userName = hurrevacSettings['HazusUserName']
    password = hurrevacSettings['HazusPassword']
    try:
        engine = create_engine('mssql+pyodbc://'+userName+':'+password+'@'+server+'/syHazus?driver=SQL+Server')
        conn = engine.connect()
    except:
        popupmsg("Error connecting to Hazus SQL Server. Check your Settings.json")
    huScenarioDoesntExist = CheckScenarioName(huScenarioName)
    if huScenarioDoesntExist:
        print(f'scenario "{huScenarioName}" does not exist in huScenario, proceed')
        try:
            huScenario.to_sql(name="huScenario", con=conn, if_exists='append', index=False)
            huStormTrack.to_sql(name="huStormTrack", con=conn, if_exists='append', index=False)
            popupmsgNextSteps(f'''Scenario "{huScenarioName}" is now available in Hazus.
                  
Please build or open an existing region and:
1. Select “{huScenarioName}”
2. Choose “Edit” so that Hazus will check and validate imported data.
3. Select Next and proceed through Hazus wizard until new scenario is saved.''')
        except:
            popupmsg(f"Error loading {huScenarioName} into Hazus.")

# #Test some of the code above...
if __name__ == "__main__":
    popupmsgNextSteps("Test error message")
