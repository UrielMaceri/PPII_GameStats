@echo off
setlocal

set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "PYTHON=%BACKEND%\.venv\Scripts\python.exe"

echo ==========================================
echo  GameStats - Preparando base de datos
echo ==========================================
echo.

if not exist "%PYTHON%" (
    echo Creando entorno virtual de Python...
    python -m venv "%BACKEND%\.venv"
    if errorlevel 1 (
        echo.
        echo [ERROR] No se pudo crear el entorno virtual. Verifica la instalacion de Python.
        if /i not "%~1"=="nopause" pause
        exit /b 1
    )
)

"%PYTHON%" -c "import fastapi, sqlalchemy, uvicorn" >nul 2>nul
if errorlevel 1 (
    echo Instalando dependencias del backend...
    "%PYTHON%" -m pip install -r "%BACKEND%\requirements.txt"
    if errorlevel 1 (
        echo.
        echo [ERROR] Fallo la instalacion del backend. Revisa los mensajes de arriba.
        if /i not "%~1"=="nopause" pause
        exit /b 1
    )
)

pushd "%BACKEND%"
"%PYTHON%" -m data.import_consoles
set "RESULT=%ERRORLEVEL%"
popd

if not "%RESULT%"=="0" (
    echo.
    echo [ERROR] No se pudo preparar la base de datos.
    if /i not "%~1"=="nopause" pause
    exit /b %RESULT%
)

echo.
echo [OK] Base de datos creada o actualizada sin borrar los datos existentes.
if /i not "%~1"=="nopause" pause
endlocal
