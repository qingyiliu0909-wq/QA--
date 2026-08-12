@echo off
chcp 65001 >nul
cd /d "%~dp0"

set PYTHON=%~dp0Python311\python.exe

if not exist "%PYTHON%" (
    echo ========================================
    echo  EM Asset Naming Rules Check
    echo ========================================
    echo.
    echo  [ERROR] Python not found.
    echo  Expected: %PYTHON%
    echo.
    echo  Please copy the Python311 folder to Validation\.
    echo.
    pause
    exit /b 1
)

echo ========================================
echo  EM Asset Naming Rules Check
echo ========================================
echo.
"%PYTHON%" check_naming_rules.py %*
echo.
pause
