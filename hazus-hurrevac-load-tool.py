try:
    from subprocess import call
    call('CALL conda.bat activate hazus_env & start /min python src/hurrevac_gui.py', shell=True)
except:
    try:
        raw_input()
    except:
        input()
    
try:
    from subprocess import check_call
    check_call('CALL conda.bat activate hazus_env && python .\src\hurrevac_gui.py', shell=True)
except:
    raw_input()