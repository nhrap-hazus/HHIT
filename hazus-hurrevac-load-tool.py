from subprocess import call
import time

try:
    call('CALL conda.bat activate hazus_env & start /min python ./src/hurrevac_run.py', shell=True)
    time.sleep(5)
except:
    print('something went wrong')
    time.sleep(5)