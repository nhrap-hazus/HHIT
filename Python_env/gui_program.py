# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 13:01:01 2020

@author: Colin Lindeman

Not intended to be imported into another script or gui.
"""
print('starting imports...')
#This area is slow
import re

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True

try:
    '''Hurrevac supporting scripts'''
    import hurrevac_main
    import hurrevac_storms
except ImportError:
    print('Failed importing supporting Hurrevac scripts')

try:
    '''for windows 10 4k screens'''
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except ImportError:
    print('Failed importing ctypes windll for windows 10 4k screens')

print('finished imports')

def center(win):
    #https://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter
    """
    centers a tkinter window
    :param win: the root or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

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
    popup.iconbitmap('./Python_env/assets/images/ICO/24px.ico')
    popup.mainloop()

def vp_start_gui():
    '''Starting point when module is the main routine.'''
    #what does this do?global val, w, root???
    global val, w, root
    root = tk.Tk()
        
    #what does this do?
    print("starting top...")
    top = Hazus_HurrEvac_HVX_ETL(root)
    print("finished top.")
    print("starting mainloop...")
    root.lift()
    root.mainloop()


class Hazus_HurrEvac_HVX_ETL():
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        top.title("Hazus Hurricane Import Tool")
        top.resizable(0,0)
        
        def getStormNames(self):
            '''Get type, basin, year then get a tuple of those storms'''
            stormTypes = []
            if self.ActiveCheckbuttonState.get() == True:
                stormTypes.append("Active")
            if self.HistoricalCheckbuttonState.get() == True:
                stormTypes.append("Historical")
            if self.ExerciseCheckbuttonState.get() == True:
                stormTypes.append("Exercise")
            if self.SimulatedCheckbuttonState.get() == True:
                stormTypes.append("Simulated")
            stormBasin = self.BasinCombobox.get()
            stormYear = self.YearCombobox.get()
            stormNames = self.storms.GetStormNames(stormTypes, stormBasin, stormYear)
            self.StormCombobox.config(values=stormNames)
            
        def updateStormNames(event):
            '''clear StormCombobox selection when parameters change'''
            self.StormCombobox.set('')
            self.StormCombobox.config(values=getStormNames(self))
            
        def updateStormNamesCheckBox():
            '''clear StormCombobox selection when parameters change'''
            self.StormCombobox.set('')
            self.StormCombobox.config(values=getStormNames(self))

        def clearStormComboboxSelection(event):
            self.StormCombobox.set('')
            
        def deleteStormIdEntry(event):
            self.StormIdEntry.delete(0, 'end')
            
        def checkButtonDefaultSettings(stormTypes):
            if 'Active' in stormTypes:
                self.ActiveCheckbutton.select()
            if 'Historical' in stormTypes:
                self.HistoricalCheckbutton.select()
            if 'Exercise' in stormTypes:
                self.ExerciseCheckbutton.select()
            if 'Simulated' in stormTypes:
                self.SimulatedCheckbutton.select()
        
        def exportHazus():
            '''get NameCombo selection (parse out the stormId from the stormLabel)'''
            try:
                StormId_NameCombo = self.StormComboboxVar.get()
                StormId_NameCombo = re.findall(".+\[(.+)\]", StormId_NameCombo)
                StormId_NameCombo = StormId_NameCombo[0]
            except:
                StormId_NameCombo = None
            '''get StormIdEntry entry'''
            try:
                StormId_StormEntry = self.StormIdEntry.get()
            except:
                StormId_StormEntry = None
            '''use whichever is available, should only be one'''
            if StormId_NameCombo:
                StormId = StormId_NameCombo
            elif StormId_StormEntry:
                StormId = StormId_StormEntry
            else:
                StormId = None
                print("No storm id selected or entered.")
                popupmsg("No storm id selected or entered.")
            if StormId:
                '''Creat a storm object, get storm web api json, process json to create dataframes, export to sql server'''
                self.storm = hurrevac_storms.StormInfo()
                self.storm.GetStormJSON(StormId)
                self.storm.GetStormDataframe(self.storm.JSON)
                hurrevac_main.ExportToHazus(self.storm.huScenarioName, self.storm.huScenario, self.storm.huStormTrack)
        
        '''Get Storms values to prepopulate lists...'''
        print('get storm values...')
        self.storms = hurrevac_storms.StormsInfo()
        print('got storm values.')
        self.stormTypes = tuple(self.storms.types)
        self.stormBasins = tuple(self.storms.basins)
        self.stormYears = tuple(self.storms.years)
        
        #Title
        self.LabelTitle = tk.Label(top, font=("Tahoma", "18"))
        self.LabelTitle.configure(text='''Hazus Hurricane Import Tool''')
        self.LabelTitle.grid(row=0, column=0, padx=10, pady=10)

        #SubTitle
        self.LabelSubTitle = tk.Label(top, font=("Tahoma", "16"))
        self.LabelSubTitle.configure(text='''Hurrevac HVX''')
        self.LabelSubTitle.grid(row=1, column=0, padx=10, pady=10)
        
        #Select a Storm frame
        self.LabelframeSelectStorm = tk.LabelFrame(top, font=("Tahoma", "12"), labelanchor='n', borderwidth=4)
        self.LabelframeSelectStorm.configure(text='''SELECT A STORM''')
        self.LabelframeSelectStorm.grid(row=2, column=0, padx=20, pady=20)
        
        self.LabelframeSelectStormType = tk.LabelFrame(self.LabelframeSelectStorm, font=("Tahoma", "12"), borderwidth=0)
        self.LabelframeSelectStormType.configure(text='''Choose one or more Storm Types to include in the Storms list:''')
        self.LabelframeSelectStormType.grid(row=0, column=0, padx=10, pady=10)

        self.ActiveCheckbuttonState = tk.BooleanVar()
        self.ActiveCheckbutton = tk.Checkbutton(self.LabelframeSelectStormType, font=("Tahoma", "12"))
        self.ActiveCheckbutton.configure(text='''Active''')
        self.ActiveCheckbutton.configure(variable=self.ActiveCheckbuttonState)
        self.ActiveCheckbutton.configure(command=updateStormNamesCheckBox)
        self.ActiveCheckbutton.grid(row=0, column=0, padx=10, pady=10,)
        
        self.HistoricalCheckbuttonState = tk.BooleanVar()
        self.HistoricalCheckbutton = tk.Checkbutton(self.LabelframeSelectStormType, font=("Tahoma", "12"))
        self.HistoricalCheckbutton.configure(text='''Historical''')
        self.HistoricalCheckbutton.configure(variable=self.HistoricalCheckbuttonState)
        self.HistoricalCheckbutton.configure(command=updateStormNamesCheckBox)
        self.HistoricalCheckbutton.grid(row=0, column=1, padx=10, pady=10,)
        
        self.ExerciseCheckbuttonState = tk.BooleanVar()
        self.ExerciseCheckbutton = tk.Checkbutton(self.LabelframeSelectStormType, font=("Tahoma", "12"))
        self.ExerciseCheckbutton.configure(text='''Exercise''')
        self.ExerciseCheckbutton.configure(variable=self.ExerciseCheckbuttonState)
        self.ExerciseCheckbutton.configure(command=updateStormNamesCheckBox)
        self.ExerciseCheckbutton.grid(row=0, column=2, padx=10, pady=10,)
        
        self.SimulatedCheckbuttonState = tk.BooleanVar()
        self.SimulatedCheckbutton = tk.Checkbutton(self.LabelframeSelectStormType, font=("Tahoma", "12"))
        self.SimulatedCheckbutton.configure(text='''Simulated''')
        self.SimulatedCheckbutton.configure(variable=self.SimulatedCheckbuttonState)
        self.SimulatedCheckbutton.configure(command=updateStormNamesCheckBox)
        self.SimulatedCheckbutton.grid(row=0, column=3, padx=10, pady=10,)
        
        '''set default checkbox settings from config file...'''
        checkButtonDefaultSettings(self.stormTypes)
        
        self.LabelframeSelectStormLists = tk.LabelFrame(self.LabelframeSelectStorm, font=("Tahoma", "12"), borderwidth=0)
        self.LabelframeSelectStormLists.configure(text='''Choose a Basin and Year to generate a list of Storms, then select a Storm and click "Load to Hazus":''')
        self.LabelframeSelectStormLists.grid(row=1, column=0, padx=10, pady=10)
       
        self.BasinCombobox = ttk.Combobox(self.LabelframeSelectStormLists, font=("Tahoma", "12"), width=17)
        self.BasinCombobox.configure(values=self.stormBasins)
        self.BasinCombobox.configure(state='readonly')
        self.BasinCombobox.current(0)
        self.BasinCombobox.bind('<<ComboboxSelected>>', updateStormNames)
        self.BasinCombobox.grid(row=0, column=0, padx=10, pady=10)
        
        self.YearCombobox = ttk.Combobox(self.LabelframeSelectStormLists, font=("Tahoma", "12"), width=6)
        self.YearComboboxvalue_list = self.stormYears
        self.YearCombobox.configure(values=self.YearComboboxvalue_list)
        self.YearCombobox.configure(state='readonly')
        self.YearCombobox.current(0)
        self.YearCombobox.bind('<<ComboboxSelected>>', updateStormNames)
        self.YearCombobox.grid(row=0, column=1, padx=10, pady=10)
        
        self.StormCombobox = ttk.Combobox(self.LabelframeSelectStormLists, font=("Tahoma", "12"), width=35)
        self.StormComboboxVar = tk.StringVar()
        self.StormCombobox.configure(textvariable=self.StormComboboxVar)
        self.StormCombobox.configure(values=self.StormComboboxVar)
        ''''Populate the StormCombobox with storms from default parameters'''
        getStormNames(self)
        self.StormCombobox.configure(state='readonly')
        self.StormCombobox.current(0)
        ''''Clear the StormIdEntry when Storm is seleted in StormCombobox'''
        self.StormCombobox.bind('<<ComboboxSelected>>', deleteStormIdEntry)
        self.StormCombobox.grid(row=0, column=2, padx=10, pady=10)
        
        self.LabelInfoText = tk.Label(self.LabelframeSelectStorm, font=("Tahoma", "12", "italic"), borderwidth=0)
        self.LabelInfoText.configure(text='''You will need to reload this program to see new storms in the list.''')
        self.LabelInfoText.grid(row=3, column=0, padx=10, pady=10)
        
        #OR label
        self.LabelOR = tk.Label(top, font=("Tahoma", "14", "bold"))
        self.LabelOR.configure(text='''OR''')
        self.LabelOR.grid(row=3, column=0, padx=20, pady=20, columnspan=2)
        
        #Enter a Storm ID Frame
        self.LabelframeEnterStorm = tk.LabelFrame(top, font=("Tahoma", "12"), labelanchor='n', borderwidth=4)
        self.LabelframeEnterStorm.configure(text='''ENTER A STORM ID''')
        self.LabelframeEnterStorm.grid(row=4, column=0, padx=20, pady=20)
        
        self.LabelEnterStormID = tk.Label(self.LabelframeEnterStorm, font=("Tahoma", "12"))
        self.LabelEnterStormID.configure(text='''If you know the Storm's Hurrevac HVX ID (I.E. "al012020"), enter it here and click "Load to Hazus":''')
        self.LabelEnterStormID.grid(row=0, column=0, padx=10, pady=10)
                                
        self.StormIdEntry = tk.Entry(self.LabelframeEnterStorm, font=("Tahoma", "12"), width=10)
        self.StormIdEntryVar = tk.StringVar()
        self.StormIdEntry.configure(textvariable=self.StormIdEntryVar)
        ''''Clear the StormCombobox selection when users enters anything in StormIdEntry'''
        self.StormIdEntry.bind('<Key>', clearStormComboboxSelection)
        self.StormIdEntry.grid(row=1, column=0, padx=10, pady=10)
        
        #Buttons
        self.LabelframeButtons = tk.LabelFrame(top, borderwidth=0)
        self.LabelframeButtons.grid(row=5, column=0, padx=10, pady=10)
        
        self.LoadToHazusButton = tk.Button(self.LabelframeButtons, font=("Tahoma", "12"))
        self.LoadToHazusButton.configure(text='''Load to Hazus''')
        self.LoadToHazusButton.configure(command=exportHazus)
        self.LoadToHazusButton.grid(row=0, column=0, padx=10, pady=10, sticky='e')

        self.QuitButton = tk.Button(self.LabelframeButtons, font=("Tahoma", "12"))
        self.QuitButton.configure(text='''Quit''')
        self.QuitButton.configure(command=root.destroy)
        self.QuitButton.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        
        #center gui on screen after building GUI...
        center(root)
        
        top.iconbitmap('./Python_env/assets/images/ICO/24px.ico')
        
if __name__ == '__main__':
    print('starting gui...')
    vp_start_gui()
    print('gui started.')
