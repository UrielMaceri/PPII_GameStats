@echo off
setlocal

set "ROOT=%~dp0"

echo ==========================================
echo  GameStats - Levantando backend y frontend
echo ==========================================
echo.

REM Crear el entorno virtual del backend si todavía no existe
if not exist "%ROOT%backend\.venv\Scripts\python.exe" (
    echo Creando entorno virtual de Python...
    python -m venv "%ROOT%backend\.venv"
    if errorlevel 1 (
        echo.
        echo [ERROR] No se pudo crear el entorno virtual. Verifica la instalacion de Python.
        pause
        exit /b 1
    )
)

REM Instalar dependencias del backend en la primera ejecucion
if not exist "%ROOT%backend\.venv\Scripts\uvicorn.exe" (
    echo Instalando dependencias del backend...
    "%ROOT%backend\.venv\Scripts\python.exe" -m pip install -r "%ROOT%backend\requirements.txt"
    if errorlevel 1 (
        echo.
        echo [ERROR] Fallo la instalacion del backend. Revisa los mensajes de arriba.
        pause
        exit /b 1
    )
    echo.
)

REM Primera ejecucion: instalar dependencias del frontend si faltan
if not exist "%ROOT%frontend\node_modules" (
    echo Primera ejecucion: instalando dependencias del frontend...
    pushd "%ROOT%frontend"
    call npm install
    if errorlevel 1 (
        echo.
        echo [ERROR] Fallo npm install. Revisa los mensajes de arriba.
        popd
        pause
        exit /b 1
    )
    popd
    echo.
)

REM Cada servicio corre en su propia ventana
start "GameStats API" /d "%ROOT%backend" cmd /k ""%ROOT%backend\.venv\Scripts\python.exe" -m uvicorn main:app --reload"
start "GameStats Frontend" /d "%ROOT%frontend" cmd /k npm run dev

echo Backend y frontend iniciados en ventanas separadas.
echo.
echo   Frontend: http://localhost:5173
echo   API:      http://127.0.0.1:8000/docs
echo.
echo Para detenerlos, presiona Ctrl+C o cierra cada ventana.
endlocal