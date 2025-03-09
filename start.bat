COLOR 90
@echo off
setlocal

:: Minimalizacja okna CMD na starcie za pomocą PowerShella
powershell -Command "$wshell = New-Object -ComObject WScript.Shell; $wshell.AppActivate('cmd.exe'); $wshell.SendKeys('%{SPACE}N')" >nul 2>&1

:: Ścieżka do folderu aplikacji (usuwamy końcowy ukośnik, jeśli istnieje)
set "APP_DIR=%~dp0"
if %APP_DIR:~-1%==\ set "APP_DIR=%APP_DIR:~0,-1%"

set "DROPBOX_URL=https://www.dropbox.com/scl/fi/55p09zpauaiq2toroy1h5/pliki_aplikacji.zip?rlkey=wf1hxnkmnvjnx0k05bl11tw1x&st=hjiq7bpa&dl=1"
set "ZIP_FILE=%TEMP%\pliki_aplikacji.zip"

:: Pobieranie pliku
echo Pobieram aktualizacje...
curl -L "%DROPBOX_URL%" -o "%ZIP_FILE%">nul

:: Sprawdzenie, czy plik istnieje i jego rozmiar
if not exist "%ZIP_FILE%" (
    echo Plik nie został pobrany!
    pause
    exit /b
)
for %%I in ("%ZIP_FILE%") do set "FILE_SIZE=%%~zI"

:: Tworzenie skryptu Pythona do rozpakowywania
echo import zipfile, os > "%TEMP%\extract.py"
echo zip_path = r"%ZIP_FILE%" >> "%TEMP%\extract.py"
echo extract_path = r"%APP_DIR%" >> "%TEMP%\extract.py"
echo print(f"Plik: {zip_path}, Rozpakowuje do: {extract_path}") >> "%TEMP%\extract.py"
echo if not os.path.exists(zip_path): print("Plik ZIP nie istnieje!"); exit(1) >> "%TEMP%\extract.py"
echo try: >> "%TEMP%\extract.py"
echo     with zipfile.ZipFile(zip_path, 'r') as zip_ref: >> "%TEMP%\extract.py"
echo         zip_ref.extractall(extract_path) >> "%TEMP%\extract.py"
echo     print("Rozpakowano pomyślnie") >> "%TEMP%\extract.py"
echo except Exception as e: >> "%TEMP%\extract.py"
echo     print(f"Błąd: {e}") >> "%TEMP%\extract.py"
echo     exit(1) >> "%TEMP%\extract.py"

:: Rozpakowanie
echo Rozpakowuje plik...
python "%TEMP%\extract.py" 2> "%TEMP%\error.txt"
if errorlevel 1 (
    echo Błąd rozpakowania!
    type "%TEMP%\error.txt"
    pause
    exit /b
)

:: Usuwanie plików tymczasowych
del "%ZIP_FILE%"
del "%TEMP%\extract.py"

echo Aktualizacja zakończona.
cd /d "%~dp0" & call venv\Scripts\activate & start /min python menu.py
exit