@echo off
cd /d "%~dp0"
echo Compilando WhatsApp Backup Viewer...
echo.

if exist "%USERPROFILE%\anaconda3\python.exe" (
    set PYTHON="%USERPROFILE%\anaconda3\python.exe"
    set PYINSTALLER="%USERPROFILE%\anaconda3\Scripts\pyinstaller.exe"
) else (
    set PYTHON=python
    set PYINSTALLER=pyinstaller
)

echo Generando version info...
%PYTHON% version_info.py

echo Ejecutando PyInstaller...
%PYINSTALLER% "WhatsApp Viewer.spec" --noconfirm

if errorlevel 1 (
    echo.
    echo Error al compilar. Asegurate de tener Python y las dependencias instaladas.
    pause
    exit /b 1
)

echo.
echo Creando estructura...
if not exist "dist\chats" mkdir "dist\chats"

echo.
echo Firmando ejecutable...
powershell -NoProfile -Command "$cert = Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert | Where-Object { $_.Subject -like '*WhatsApp Backup Viewer*' } | Select-Object -First 1; if ($cert) { Set-AuthenticodeSignature -FilePath 'dist\WhatsApp Viewer.exe' -Certificate $cert -TimestampServer 'http://timestamp.digicert.com' -HashAlgorithm SHA256 | Select-Object StatusMessage } else { Write-Warning 'No se encontro certificado. Ejecuta create_cert.ps1 primero.' }"

echo.
echo ========================================
echo  Listo!
echo  Ejecutable: dist\WhatsApp Viewer.exe
echo  Coloca tus chats en: dist\chats\
echo ========================================
