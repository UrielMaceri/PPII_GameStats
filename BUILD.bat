@echo off
setlocal

echo ==========================================
echo  GameStats - Verificando backend Python
echo ==========================================
echo.

python -m compileall -q "%~dp0backend"
if errorlevel 1 (
    echo.
    echo [ERROR] La verificacion fallo. Revisa los mensajes de arriba.
    if /i not "%~1"=="nopause" pause
    exit /b 1
)

echo.
echo [OK] Verificacion sintactica exitosa.
if /i not "%~1"=="nopause" pause
endlocal