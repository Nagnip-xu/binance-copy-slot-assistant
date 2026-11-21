@echo off
chcp 65001 >nul
setlocal
pushd "%~dp0"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0bootstrap_python.ps1" -EntryScript "launcher.py"
set "APP_EXIT=%ERRORLEVEL%"
if not "%APP_EXIT%"=="0" (
  echo.
  echo 程序启动失败，退出代码：%APP_EXIT%
  echo 请查看“Python自动安装错误.log”或“启动错误.log”。
  pause
)
popd
endlocal
