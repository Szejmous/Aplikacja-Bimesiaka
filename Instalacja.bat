@echo off
:: Sprawdzamy, czy skrypt działa z uprawnieniami administratora
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Uruchamiam jako administrator...
    :: Ponowne uruchomienie skryptu jako administrator
    powershell -Command "Start-Process '%~f0' -Verb runAs"
    exit /b
)
set TARGET_PATH=%~dp0start.bat
set ICON_PATH=%~dp0start_ikona.ico


set SHORTCUT_PATH=%USERPROFILE%\Desktop\BIMESIAK.lnk
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath='%TARGET_PATH%'; $s.WorkingDirectory='%~dp0'; $s.IconLocation='%ICON_PATH%'; $s.Save()"

set START_MENU_PATH=%APPDATA%\Microsoft\Windows\Start Menu\Programs\BIMESIAK.lnk
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%START_MENU_PATH%'); $s.TargetPath='%TARGET_PATH%'; $s.WorkingDirectory='%~dp0'; $s.IconLocation='%ICON_PATH%'; $s.Save()"

@echo off

chcp 65001 >nul 2>&1

COLOR 90
cd /d "%~dp0"
.\\python3132.exe

REM Zapisuje bieżący folder, w którym jest uruchomiony skrypt .bat

set "CURRENT_DIR=%CD%"

cd /d C:\Windows\System32

set "CURRENT_PATH=%PATH%"

REM Ścieżka do katalogu Scripts
set "SCRIPTS_PATH=C:\Users\%USERNAME%\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts"

echo %CURRENT_PATH% | findstr /I /C:"%SCRIPTS_PATH%" >nul

if %errorlevel% neq 0 (

    set "PATH=%CURRENT_PATH%;%SCRIPTS_PATH%"
    echo Dodano %SCRIPTS_PATH% do PATH w bieżącej sesji.
    REM Używa setx, by na stałe dodać ścieżkę do systemowego PATH
    cmd /c setx PATH "%PATH%" /M
    echo Ścieżka została dodana na stałe! Uruchom ponownie komputer, aby zmiany zadziałały.

)
echo Poczekaj, trwa instalacja...


cd /d "%CURRENT_DIR%"
@echo off
pip install --upgrade -r requirements.txt > nul

echo [43m[30m==========================================================
echo ==    Instalacja zakończona poprawnie.                    ==
echo ==    Uruchom program za pomocą pliku "start".            ==
echo ==========================================================[0m
echo Wciśnij enter aby zamknąć.
pause > nul





