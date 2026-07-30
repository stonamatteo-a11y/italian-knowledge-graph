@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-ikg.ps1" %*
set "IKG_EXIT_CODE=%ERRORLEVEL%"
if not "%IKG_EXIT_CODE%"=="0" (
  echo.
  echo IKG could not start. Exit code: %IKG_EXIT_CODE%
  pause
)
exit /b %IKG_EXIT_CODE%
