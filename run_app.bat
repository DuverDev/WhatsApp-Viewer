@echo off
cd /d "%~dp0"

if exist "%USERPROFILE%\anaconda3\python.exe" (
    set PYTHON="%USERPROFILE%\anaconda3\python.exe"
) else (
    where py >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        set PYTHON=py
    ) else (
        set PYTHON=python
    )
)

%PYTHON% -c "import flask; import webview" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Instalando dependencias...
    %PYTHON% -m pip install -r requirements.txt
    echo.
)

%PYTHON% app.py

if errorlevel 1 (
    echo.
    echo No se pudo iniciar la app.
    echo Asegurate de tener Python instalado y que el comando "python" o "py" este disponible.
    echo.
    pause
)
