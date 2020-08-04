try:
    from manage import internetConnected, checkForHazPyUpdates, checkForToolUpdates
    if internetConnected():
        from subprocess import check_call
        check_call('CALL conda.bat activate hazus_env && python src\hurrevac_gui.py', shell=True)

except:
    import ctypes
    messageBox = ctypes.windll.user32.MessageBoxW
    messageBox(0,"The tool was unable to open. You need internet connection for this tool to update. If this problem persists, contact hazus-support@riskmapcds.com","Hazus", 0x1000)
