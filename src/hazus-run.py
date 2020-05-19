from subprocess import check_call
import time

try:
    check_call('CALL conda.bat activate hazus_env && python hurrevac_gui.py', shell=True)
    time.sleep(5)
except:
    check_call('activate hazus_env && python gui_program.py', shell=True)
    time.sleep(5)