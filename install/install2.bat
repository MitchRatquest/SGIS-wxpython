@ ECHO off
@ REM off
C:\python27\python.exe .\get_pip.py
C:\python27\python.exe .\ez_setup.py
pip install image
pip install -r requirements.txt
pause
