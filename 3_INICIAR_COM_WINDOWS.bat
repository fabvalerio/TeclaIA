@echo off
title Tecla IA - Inicializacao Automatica

echo.
echo ==========================================
echo   TECLA IA - Configurar Inicio Automatico
echo ==========================================
echo.
echo  Isso fara o Tecla IA iniciar automaticamente com o Windows.
echo.

set "SCRIPT_DIR=%~dp0"
set "BAT_FILE=%SCRIPT_DIR%2_INICIAR_COMO_ADMIN.bat"
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT=%STARTUP_DIR%\TeclaIA.lnk"

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $sc = $ws.CreateShortcut('%SHORTCUT%'); $sc.TargetPath = '%BAT_FILE%'; $sc.WorkingDirectory = '%SCRIPT_DIR%'; $sc.Description = 'Tecla IA - Expansor de Texto'; $sc.Save()"

if exist "%SHORTCUT%" (
    echo  [OK] Tecla IA adicionado a inicializacao do Windows!
    echo.
    echo  Para remover, delete o arquivo:
    echo  %SHORTCUT%
) else (
    echo  [ERRO] Nao foi possivel criar o atalho de inicializacao.
    echo         Tente executar como Administrador.
)

echo.
pause
