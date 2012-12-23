@ECHO OFF

SET adapter="ローカル エリア接続"

:start
ECHO notice that this script requires administrator previledge.
SET /p mode="configure static (y/n)? "
IF "%mode%" == "y" GOTO configure_static
IF "%mode%" == "n" GOTO configure_dhcp
GOTO start

:configure_static
ECHO configure static.
SET /p address="address/prefix? "
SET /p gateway="gateway? "
SET /p nameserver="nameserver (default: %gateway%)? "
IF "%nameserver%"=="" SET nameserver="%gateway%"
netsh interface ip set address %adapter% static address=%address% gateway=%gateway% gwmetric=1
netsh interface ip set dns %adapter% static address=%nameserver% register=primary validate=no
TIMEOUT 5
GOTO show_setting

:configure_dhcp
ECHO configure dhcp.
netsh interface ip set address %adapter% dhcp
netsh interface ip set dns %adapter% dhcp
TIMEOUT 5
GOTO show_setting

:show_setting
netsh interface ip show address %adapter%
netsh interface ip show dns %adapter%
PAUSE
EXIT
