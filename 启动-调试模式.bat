@echo off
chcp 65001 >nul
pushd "%~dp0"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0bootstrap_python.ps1" -EntryScript "launcher.py"
echo.
echo 程序退出代码：%ERRORLEVEL%
popd
pause
