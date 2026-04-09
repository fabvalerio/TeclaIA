@echo off
title Tecla IA

:: Re-lanca como Administrador (necessario para captura global de teclas)
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Solicitando permissao de Administrador...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: Ja esta rodando como admin - inicia o aplicativo
echo.
echo ==========================================
echo   TECLA IA - Iniciando...
echo ==========================================
echo.
echo  Atalho: CTRL+ALT+I
echo  O icone aparecera na bandeja do sistema (proximo ao relogio).
echo  Para sair: clique com o botao direito no icone e clique Sair
echo.

cd /d "%~dp0"
python ia_atalho.py

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha ao iniciar. Execute 1_INSTALAR.bat primeiro.
    pause
)
