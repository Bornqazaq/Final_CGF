@echo off
if exist "%~dp0dist\Windows-x64\LaserVaultHeist.exe" (
  start "" "%~dp0dist\Windows-x64\LaserVaultHeist.exe"
  exit /b
)
if exist "%~dp0play\LaserVaultHeist.exe" (
  start "" "%~dp0play\LaserVaultHeist.exe"
  exit /b
)
if exist "%~dp0build\LaserVaultHeist.exe" (
  start "" "%~dp0build\LaserVaultHeist.exe"
  exit /b
)
echo Build the project using README.md, or download the Windows release ZIP.
pause
