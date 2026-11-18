@echo off
setlocal
cd /d "%~dp0"
echo Compilando WhatsApp Backup Viewer...
echo.

if exist ".venv\Scripts\python.exe" (
    set "PYTHON=.venv\Scripts\python.exe"
) else if exist "..\.venv\Scripts\python.exe" (
    set "PYTHON=..\.venv\Scripts\python.exe"
) else if exist "%USERPROFILE%\anaconda3\python.exe" (
    set "PYTHON=%USERPROFILE%\anaconda3\python.exe"
) else (
    set "PYTHON=python"
)

echo Generando iconos...
"%PYTHON%" gen_icon.py
if errorlevel 1 (
    echo ERROR: Fallo gen_icon.py
    exit /b 1
)

echo Generando version info...
"%PYTHON%" version_info.py
if errorlevel 1 (
    echo ERROR: Fallo version_info.py
    exit /b 1
)

echo Ejecutando PyInstaller...
"%PYTHON%" -m PyInstaller "WhatsApp Viewer.spec" --noconfirm
if errorlevel 1 (
    echo.
    echo Error al compilar. Asegurate de tener Python y las dependencias instaladas.
    exit /b 1
)

echo.
echo Creando estructura y calculando SHA-256...
if not exist "dist\chats" mkdir "dist\chats"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $f='dist\WhatsApp Viewer.exe'; $h=(Get-FileHash -LiteralPath $f -Algorithm SHA256).Hash.ToLowerInvariant(); $l=[System.IO.Path]::GetFileName($f); ($h+' *'+$l) | Set-Content -LiteralPath ($f+'.sha256') -Encoding ascii -NoNewline; Write-Host ('SHA-256 ('+$l+'): '+$h)"
if errorlevel 1 (
    echo ERROR: No se pudo calcular SHA-256.
    exit /b 1
)

echo.
echo ========================================
echo  Listo!
echo  Ejecutable: dist\WhatsApp Viewer.exe
echo  Checksum:   dist\WhatsApp Viewer.exe.sha256
echo  Coloca tus chats en: dist\chats\
echo ========================================
exit /b 0
