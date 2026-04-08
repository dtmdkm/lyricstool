@echo off
setlocal
echo ============================================
echo   LyricsSRT Converter - Windows Build
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python khong tim thay. Vui long cai Python 3.10+
    pause & exit /b 1
)

echo [1/3] Cai dat thu vien...
pip install -r requirements.txt
pip install pyinstaller
if errorlevel 1 ( echo [ERROR] Cai dat that bai & pause & exit /b 1 )

echo.
echo [2/3] Dang build ung dung...
pyinstaller build.spec --noconfirm
if errorlevel 1 ( echo [ERROR] Build that bai & pause & exit /b 1 )

echo.
echo [3/3] Nen thanh file ZIP...
powershell -Command "Compress-Archive -Force -Path dist\LyricsSRTConverter -DestinationPath LyricsSRTConverter-Windows.zip"

echo.
echo ============================================
echo   HOAN THANH!
echo   File ung dung:  dist\LyricsSRTConverter\LyricsSRTConverter.exe
echo   File ZIP:       LyricsSRTConverter-Windows.zip
echo ============================================
pause
