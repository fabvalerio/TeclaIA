@echo off
title Tecla IA - Gerando EXE

echo.
echo ==========================================
echo   TECLA IA - Criando executavel .EXE
echo ==========================================
echo.
echo  Isso pode levar 1 a 3 minutos...
echo.

cd /d "%~dp0"

:: Verifica Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado. Execute 1_INSTALAR.bat primeiro.
    pause
    exit /b 1
)

:: Instala PyInstaller
echo [1/3] Instalando PyInstaller...
pip install pyinstaller --quiet
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar PyInstaller.
    pause
    exit /b 1
)
echo [OK] PyInstaller instalado.
echo.

:: Tenta instalar Pillow + pystray para o icone na bandeja
echo [2/3] Instalando dependencias visuais...
pip install Pillow pystray --only-binary :all: --quiet
echo [OK] Feito (avisos sao normais se nao suportado na sua versao do Python).
echo.

:: Gera o EXE
echo [3/3] Gerando TeclaIA.exe...
echo.

python -m PyInstaller ^
    --onefile ^
    --noconsole ^
    --uac-admin ^
    --name TeclaIA ^
    --clean ^
    --distpath "%~dp0dist" ^
    --workpath "%~dp0build_tmp" ^
    --specpath "%~dp0build_tmp" ^
    ia_atalho.py

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha ao gerar o EXE.
    echo        Veja o log acima para detalhes.
    pause
    exit /b 1
)

:: Limpeza dos arquivos temporarios de build
echo.
echo Limpando arquivos temporarios...
rmdir /s /q "%~dp0build_tmp" 2>nul

echo.
echo ==========================================
echo   EXE gerado com sucesso!
echo ==========================================
echo.
echo  Arquivo: dist\TeclaIA.exe
echo.
echo  Como distribuir:
echo    - Copie apenas o arquivo dist\TeclaIA.exe
echo    - O usuario precisara ter o Ollama instalado
echo    - Clique duplo no TeclaIA.exe para iniciar
echo    - O Windows pedira permissao de Administrador
echo      (necessario para capturar teclas globalmente)
echo.
echo  Atalhos:
echo    Ctrl+Alt+I  = Casual
echo    Ctrl+Alt+O  = Formal
echo    Ctrl+Alt+P  = Corrigir
echo    Ctrl+Alt+R  = Responder
echo    Ctrl+Alt+Z  = Desfazer
echo.
pause
