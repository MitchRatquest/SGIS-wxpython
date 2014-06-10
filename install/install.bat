mode con: cols=160 lines=78
@echo off
@REM
echo & echo                                    ,@::@@@                        & echo                                    +:;;::,@                       & echo                                   @;:::::::@                      & echo                                   @::@@':;':#@                    & echo                                   ,@@@:#'@':::+@@                 & echo                             .@@@@@@@@@@@#,,@;::::+@               & echo                            @;;;;;;;;;;@,:@+:@::::::@,             & echo                            :;;;;';;;;;;@+:;@,#@;::::+@            & echo                         +@@;;;';;;;';;;;@@@#@@:@:;:::::           & echo                       @;;@@;;;;;;;';';;;'+;;':@#@:;:::+           & echo                     .@;@;;#;;;;';;;;;;;+@,,;@::@:@:::::@          & echo                :   @:,@;@;;@#;;;+##++#@;;'+#+@::'+':::;:@         & echo              @+;;+@@@@;;;@+;;@@+,,;;;;@;;;+;;#;#@@@:::::#         & echo              +;;;;;;+;'@@,,:@,,@@+;@#;;;;;;;;;;;;@@#:::::@        & echo             @;;;;;;;';;;@;;;@@#;;@:,,+@;;;#@@@@@;;'@:@;:::@       & echo          ,@'+';';;;;;;;;:;;;;;;;#;;+@@+@@#:;;;;;#@;@'@#::::@      & echo        .@+#@#;';;;;';;;;#;',#;;;;;+;;;@;;;;;';;;;;@;;+@@;:::##    & echo      +@@@;;;@;;;'#@@;;;@@;;',@;;#;;;;;';;;;;;;;;;;;@;@''':::::@   & echo   ,@+:';;;;+@+@@+;@,@@@;;;';:,@;;;@,@@;;;;;';;;''';;';@#@:;;::'+  & echo  #:::::@@@@@;;;@;;'@;;+@;;;;;,@#;;+@;;;;;;;;';;;'';';;;:@@:::::@  & echo  '@@#@';;;::'@@@#';;'@:#';;;;;;;;;;@,;@#;;;;;;;;;;@+;;;,@@:;:::'  & echo   @..,.@@@@@':;::::',@@;;;#@+;;;;;@,#+,,@@@@@@@@@+;@@;;@@';:::::  & echo    @@@@@@,@:.:@@:::;#:;:@@::;#@@;@@@@::@,,;@@,,,,@,,@;;;@+@,.@':` & echo            @@@@,'@@@@@@@@;:;::::+::;:::::@:::@@,'@@+;;;;:+.,.,@:  & echo          @ ;  '@@'.,,,,,.,@@,::::::++'':::;::::+:;::@@;::@..,.,@  & echo           ,       @@@:.:+,...@@+',,.....'@#:::::::::::::'@...,.'  & echo                       @@@+@:@,'+.@@.@'..@,,,;:::;+#:;,,..,.,,.@   & echo                                 '@@@@@@@@@@@@,@@,@.@@.@;.,.'.@.   & echo                                             :@@@@@'..@#'@.@@@     & echo                                                  :,,`
echo Starting Installation Process for excellent pizza time expreiance
pause

set path=%path%;C:\python27;C:\python27\scripts
reg ADD "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path /t REG_EXPAND_SZ /d %path% /f

msiexec /i dependencies\python-2.7.6.msi
msiexec /i dependencies\pycurl-7.19.0.2.win32-py2.7.msi
start dependencies\paramiko-1.7.7.1.win32-py2.7.exe
start dependencies\pycrypto-2.3.win32-py2.7.exe
start dependencies\pip-1.5.4.win32-py2.7.exe
start dependencies\wxPython3.0-win32-3.0.0.0-py27.exe

echo Need to reboot the system for registry changes to take effect
echo After reboot run install2
pause
