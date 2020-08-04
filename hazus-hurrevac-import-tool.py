##from subprocess import call
##call('CALL conda.bat activate hazus_env & start /min python ./src/hurrevac_run.py', shell=True)
 
import json
from subprocess import call

try:
    # load config
    try:
        with open('./src/config.json') as configFile:
            config = json.load(configFile)
    except:
        with open('./config.json') as configFile:
            config = json.load(configFile)
 
    # check if the virtual environment has been created
    release = config['release']
    virtual_env = config[release]['virtualEnvironment']
    res = call('CALL conda.bat activate ' + virtual_env, shell=True)
    print(res)
    if res == 1:
        # create the virtual environment
        print(2)
        try:
            from src.manage import createHazPyEnvironment
        except:
            breakpoint()
        #from src.manage import createHazPyEnvironment
        print(3)
        createHazPyEnvironment()
    else:
        call('CALL conda.bat activate '+ virtual_env +
             ' && start /min python src/hurrevac_run.py', shell=True)
        call('CALL conda.bat activate '+ virtual_env +
             ' && start /min python src/update.py', shell=True)
except:
    import ctypes
    import sys
    messageBox = ctypes.windll.user32.MessageBoxW
    error = sys.exc_info()[0]
    messageBox(0, u"Unexpected error: {er} | If this problem persists, contact hazus-support@riskmapcds.com.".format(er=error), u"HazPy", 0x1000)
