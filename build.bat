@echo off
echo Compilando WhatsApp Backup Viewer...
echo.

pip install pyinstaller >nul 2>&1

echo Generando version info...
python version_info.py

pyinstaller --onefile --windowed ^
  --name "WhatsApp Viewer" ^
  --icon "app.ico" ^
  --version-file "version_info.txt" ^
  --add-data "templates;templates" ^
  --add-data "app_icon_256.png;." ^
  --hidden-import webview ^
  --hidden-import webview.platforms.winforms ^
  --hidden-import clr_loader ^
  --hidden-import pythonnet ^
  --collect-data webview ^
  --exclude-module PyQt5 ^
  --exclude-module PyQt6 ^
  --exclude-module PySide2 ^
  --exclude-module PySide6 ^
  --exclude-module tkinter ^
  --exclude-module _tkinter ^
  --exclude-module matplotlib ^
  --exclude-module numpy ^
  --exclude-module pandas ^
  --exclude-module scipy ^
  --exclude-module PIL ^
  --exclude-module IPython ^
  --exclude-module notebook ^
  --exclude-module nbformat ^
  --exclude-module nbconvert ^
  --exclude-module zmq ^
  --exclude-module tornado ^
  --exclude-module black ^
  --exclude-module pygments ^
  --exclude-module chardet ^
  --exclude-module sqlite3 ^
  --exclude-module test ^
  --exclude-module unittest ^
  app.py

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
pause
