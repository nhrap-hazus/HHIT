from subprocess import call
import time

call('CALL conda.bat activate hazus_env & start /min python ./src/hurrevac_gui.py', shell=True)
time.sleep(5)