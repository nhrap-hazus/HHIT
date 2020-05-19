
try:
    from subprocess import call
    call('CALL conda.bat activate hazus_env & start /min python hurrevac_gui.py', shell=True)
except:
    raw_input()
#try:
#    from subprocess import check_call
#    check_call('CALL conda.bat activate hazus_env && python hurrevac_gui.py', shell=True)
#except:
#    raw_input()