@echo off
setlocal

set "ROOT=%~dp0"
set "PYTHON=%ROOT%backend\.venv\Scripts\python.exe"

echo ==========================================
echo  GameStats - Levantando backend y frontend
echo ==========================================
echo.

REM Crear el entorno virtual del backend si todavía no existe
if not exist "%PYTHON%" (
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
"%PYTHON%" -c "import fastapi, sqlalchemy, uvicorn" >nul 2>nul
if errorlevel 1 (
    python -c "import fastapi, sqlalchemy, uvicorn" >nul 2>nul
    if errorlevel 1 (
        echo Instalando dependencias del backend...
        "%PYTHON%" -m pip install -r "%ROOT%backend\requirements.txt"
        if errorlevel 1 (
            echo.
            echo [ERROR] No se pudieron instalar las dependencias del backend.
            echo Verifica la conexion a Internet o instala las dependencias manualmente.
            pause
            exit /b 1
        )
    ) else (
        echo Usando dependencias disponibles en la instalacion global de Python.
        set "PYTHON=python"
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
start "GameStats API" /d "%ROOT%backend" cmd /k ""%PYTHON%" -m uvicorn main:app --reload"
start "GameStats Frontend" /d "%ROOT%frontend" cmd /k npm run dev

echo Backend y frontend iniciados en ventanas separadas.
echo.
echo   Frontend: http://localhost:5173
echo   API:      http://127.0.0.1:8000/docs
echo.
echo Para detenerlos, presiona Ctrl+C o cierra cada ventana.
endlocal