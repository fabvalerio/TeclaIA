@echo off
title Tecla IA - Instalacao

echo.
echo ==========================================
echo   TECLA IA - Instalando dependencias
echo ==========================================
echo.

:: Verifica se Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado!
    echo.
    echo  Baixe e instale o Python em:
    echo  https://www.python.org/downloads/
    echo.
    echo  IMPORTANTE: Marque "Add Python to PATH" durante a instalacao!
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado:
python --version
echo.

:: Instala dependencias principais (sem Pillow)
echo [1/2] Instalando pacotes principais...
pip install keyboard pyperclip requests

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha ao instalar dependencias principais.
    echo        Verifique sua conexao com a internet e tente novamente.
    pause
    exit /b 1
)

:: Instala Pillow + pystray (icone na bandeja) — apenas binario pre-compilado
echo.
echo [2/2] Tentando instalar icone da bandeja (Pillow + pystray)...
pip install pystray --only-binary :all: >nul 2>&1
pip install Pillow --only-binary :all: >nul 2>&1

if %errorlevel% neq 0 (
    echo [AVISO] Icone da bandeja nao disponivel para sua versao do Python.
    echo         O atalho funcionara normalmente, mas sem icone na bandeja.
) else (
    echo [OK] Icone da bandeja instalado com sucesso.
)

echo.
echo ==========================================
echo   Instalacao concluida!
echo ==========================================
echo.
echo  Proximos passos:
echo.
echo  1. Instale o Ollama (se ainda nao tiver):
echo     https://ollama.com
echo.
echo  2. Abra o Prompt de Comando e rode:
echo     ollama pull llama3.2
echo.
echo  3. Execute o arquivo:
echo     2_INICIAR_COMO_ADMIN.bat
echo.
pause
