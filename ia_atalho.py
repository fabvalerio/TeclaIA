#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TECLA IA - Expansor de Texto com Ollama
Atalho: Ctrl+Alt+I

Como usar:
  1. Clique em qualquer campo de texto
  2. Digite um texto curto (ex: "frase de bom dia")
  3. Pressione Ctrl+Alt+I
  4. Uma janela de carregamento aparece enquanto a IA processa
  5. O texto sera substituido automaticamente!
"""

import keyboard
import pyperclip
import requests
import time
import threading
import sys
import tkinter as tk
from tkinter import font as tkfont

# ================================================================
#  CONFIGURACOES - Edite aqui conforme sua preferencia
# ================================================================

ATALHO         = "ctrl+alt+i"    # Atalho de teclado
MODELO_OLLAMA  = "llama3.2"      # Modelo Ollama instalado na sua maquina
OLLAMA_URL     = "http://localhost:11434/api/generate"
TIMEOUT_API    = 60              # Tempo maximo de espera (segundos)

PROMPT_SISTEMA = (
    "Voce e um assistente que reescreve mensagens curtas como se o USUARIO estivesse "
    "enviando para outra pessoa. Voce nunca responde ao texto — voce sempre o reescreve "
    "na VOZ de quem esta enviando a mensagem.\n\n"
    "Regras obrigatorias:\n"
    "- Reescreva o texto como uma mensagem que o usuario enviaria a outra pessoa\n"
    "- NUNCA responda ao texto, mesmo que ele seja uma pergunta\n"
    "- Se o texto for uma pergunta (ex: 'voce esta ai?'), reescreva-a como uma "
    "pergunta que o usuario faz para alguem (ex: 'Oi! Por acaso voce esta ai?')\n"
    "- Se o texto for um cumprimento (ex: 'bom dia'), expanda como saudacao enviada "
    "a alguem (ex: 'Ola, bom dia! Tudo bem contigo?')\n"
    "- Mantenha o tom do texto original (formal, informal, carinhoso, profissional)\n"
    "- Responda APENAS com o texto reescrito, sem aspas, sem explicacoes, sem prefixos\n"
    "- O resultado deve soar natural, como uma mensagem real de chat ou email"
)

# ================================================================

# Tenta importar bibliotecas opcionais (bandeja do sistema)
try:
    from PIL import Image, ImageDraw, ImageFont
    import pystray
    TRAY_DISPONIVEL = True
except ImportError:
    TRAY_DISPONIVEL = False

_processando  = False
_icone_global = None


# ================================================================
#  JANELA DE CARREGAMENTO (tkinter — ja vem com Python)
# ================================================================

class JanelaCarregando:
    """
    Popup flutuante no canto inferior direito que mostra o progresso.
    Aparece ao iniciar e fecha automaticamente ao terminar.
    """

    # Cores
    COR_FUNDO       = "#1e1e2e"
    COR_TITULO      = "#cdd6f4"
    COR_TEXTO       = "#a6adc8"
    COR_DESTAQUE    = "#89b4fa"
    COR_SUCESSO     = "#a6e3a1"
    COR_ERRO        = "#f38ba8"
    COR_BORDA       = "#313244"

    SPINNER_FRAMES  = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self):
        self._root        = None
        self._lbl_spinner = None
        self._lbl_titulo  = None
        self._lbl_msg     = None
        self._spinner_idx = 0
        self._animando    = False
        self._thread      = None

    # ── Ciclo de vida ──────────────────────────────────────────────

    def mostrar(self, titulo: str = "Processando...", mensagem: str = ""):
        """Abre a janela em uma thread dedicada."""
        self._thread = threading.Thread(
            target=self._criar_janela, args=(titulo, mensagem), daemon=True
        )
        self._thread.start()
        time.sleep(0.15)   # aguarda a janela aparecer

    def atualizar(self, titulo: str = None, mensagem: str = None):
        """Atualiza textos sem fechar a janela."""
        if self._root is None:
            return
        try:
            if titulo and self._lbl_titulo:
                self._lbl_titulo.config(text=titulo)
            if mensagem is not None and self._lbl_msg:
                self._lbl_msg.config(text=mensagem)
        except Exception:
            pass

    def fechar(self, titulo_final: str = None, cor: str = None, delay: float = 1.8):
        """Mostra mensagem final por `delay` segundos e fecha."""
        try:
            if titulo_final and self._lbl_titulo:
                self._lbl_titulo.config(
                    text=titulo_final,
                    fg=cor or self.COR_SUCESSO
                )
            if self._lbl_spinner:
                icone = "✓" if (cor or "") != self.COR_ERRO else "✗"
                self._lbl_spinner.config(text=icone, fg=cor or self.COR_SUCESSO)
            self._animando = False
        except Exception:
            pass

        def _destruir():
            time.sleep(delay)
            try:
                if self._root:
                    self._root.destroy()
                    self._root = None
            except Exception:
                pass

        threading.Thread(target=_destruir, daemon=True).start()

    # ── Construção da janela ───────────────────────────────────────

    def _criar_janela(self, titulo: str, mensagem: str):
        self._root = tk.Tk()
        root = self._root

        # Sem barra de título, sempre no topo, transparente nas bordas
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-alpha", 0.95)
        root.configure(bg=self.COR_FUNDO)

        # Tamanho e posição (canto inferior direito)
        largura, altura = 320, 90
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        x  = sw - largura - 20
        y  = sh - altura - 60
        root.geometry(f"{largura}x{altura}+{x}+{y}")

        # Borda arredondada simulada com Frame interno
        frame = tk.Frame(root, bg=self.COR_BORDA, padx=1, pady=1)
        frame.pack(fill="both", expand=True)
        inner = tk.Frame(frame, bg=self.COR_FUNDO, padx=14, pady=10)
        inner.pack(fill="both", expand=True)

        # Linha superior: spinner + título
        linha1 = tk.Frame(inner, bg=self.COR_FUNDO)
        linha1.pack(fill="x")

        self._lbl_spinner = tk.Label(
            linha1, text=self.SPINNER_FRAMES[0],
            bg=self.COR_FUNDO, fg=self.COR_DESTAQUE,
            font=("Segoe UI", 14)
        )
        self._lbl_spinner.pack(side="left", padx=(0, 8))

        self._lbl_titulo = tk.Label(
            linha1, text=titulo,
            bg=self.COR_FUNDO, fg=self.COR_TITULO,
            font=("Segoe UI", 11, "bold"), anchor="w"
        )
        self._lbl_titulo.pack(side="left", fill="x", expand=True)

        # Linha inferior: mensagem de detalhe
        self._lbl_msg = tk.Label(
            inner, text=mensagem,
            bg=self.COR_FUNDO, fg=self.COR_TEXTO,
            font=("Segoe UI", 9), anchor="w",
            wraplength=280, justify="left"
        )
        self._lbl_msg.pack(fill="x", pady=(4, 0))

        # Inicia animação do spinner
        self._animando = True
        self._animar()

        root.mainloop()

    def _animar(self):
        """Atualiza o spinner a cada 80ms enquanto _animando=True."""
        if not self._animando or self._root is None:
            return
        try:
            self._spinner_idx = (self._spinner_idx + 1) % len(self.SPINNER_FRAMES)
            self._lbl_spinner.config(text=self.SPINNER_FRAMES[self._spinner_idx])
            self._root.after(80, self._animar)
        except Exception:
            pass


# ── Instância global da janela ────────────────────────────────────
_janela = JanelaCarregando()


# ================================================================
#  COMUNICACAO COM OLLAMA
# ================================================================

def verificar_ollama() -> bool:
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def expandir_texto(texto: str):
    """Retorna (sucesso: bool, resultado: str)."""
    try:
        payload = {
            "model": MODELO_OLLAMA,
            "prompt": (
                f"Reescreva esta mensagem curta como se EU estivesse enviando para outra pessoa. "
                f"Nao responda ao texto, apenas reescreva-o de forma mais completa e natural: {texto}"
            ),
            "system": PROMPT_SISTEMA,
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 300},
        }
        resp = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT_API)
        resp.raise_for_status()
        resultado = resp.json().get("response", "").strip()
        return (True, resultado) if resultado else (False, "Resposta vazia do modelo.")
    except requests.ConnectionError:
        return False, "Ollama nao esta rodando. Inicie o Ollama primeiro."
    except requests.Timeout:
        return False, "Tempo limite excedido. Modelo pode estar lento."
    except Exception as e:
        return False, f"Erro inesperado: {e}"


# ================================================================
#  LOGICA PRINCIPAL DO ATALHO
# ================================================================

def ao_pressionar_atalho():
    global _processando
    if _processando:
        return
    _processando = True
    threading.Thread(target=_executar_expansao, daemon=True).start()


def _executar_expansao():
    global _processando

    try:
        # 1. Salva clipboard original
        clip_original = pyperclip.paste()

        # 2. Seleciona tudo e copia
        pyperclip.copy("")
        time.sleep(0.15)
        keyboard.send("ctrl+a")
        time.sleep(0.2)
        keyboard.send("ctrl+c")
        time.sleep(0.4)

        texto = pyperclip.paste().strip()

        if not texto or len(texto) < 2:
            pyperclip.copy(clip_original)
            _janela.mostrar("Nada selecionado", "Clique no campo de texto e tente novamente.")
            _janela.fechar(titulo_final="Nada encontrado", cor=JanelaCarregando.COR_ERRO, delay=2)
            return

        # Texto de preview (truncado)
        preview = f'"{texto[:35]}..."' if len(texto) > 35 else f'"{texto}"'

        # 3. Abre janela de carregamento
        _janela.mostrar(
            titulo="Tecla IA — Processando",
            mensagem=f"Expandindo: {preview}"
        )

        # 4. Chama Ollama
        sucesso, resultado = expandir_texto(texto)

        if sucesso:
            # 5a. Cola o resultado
            _janela.atualizar(mensagem="Colando texto expandido...")
            pyperclip.copy(resultado)
            time.sleep(0.1)
            keyboard.send("ctrl+a")
            time.sleep(0.1)
            keyboard.send("ctrl+v")

            _janela.fechar(
                titulo_final="Pronto!  Texto expandido",
                cor=JanelaCarregando.COR_SUCESSO,
                delay=1.8
            )
            print(f"  [OK] Expandido: {resultado[:60]}...")
        else:
            # 5b. Mostra erro
            _janela.fechar(
                titulo_final=f"Erro: {resultado[:50]}",
                cor=JanelaCarregando.COR_ERRO,
                delay=3
            )
            print(f"  [ERRO] {resultado}")

        # 6. Restaura clipboard
        time.sleep(2)
        pyperclip.copy(clip_original)

    except Exception as e:
        _janela.fechar(titulo_final=f"Erro inesperado", cor=JanelaCarregando.COR_ERRO, delay=3)
        print(f"  [ERRO] {e}")
    finally:
        _processando = False


# ================================================================
#  BANDEJA DO SISTEMA (opcional — Pillow + pystray)
# ================================================================

def _criar_icone_imagem():
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([2, 2, size - 2, size - 2], fill=(40, 120, 230, 255))
    font = None
    for nome in ["arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"]:
        try:
            font = ImageFont.truetype(nome, 26)
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()
    draw.text((size // 2, size // 2), "AI", fill=(255, 255, 255, 255),
              font=font, anchor="mm")
    return img


def _sair_bandeja(icon, _item):
    icon.stop()
    sys.exit(0)


def iniciar_com_bandeja():
    global _icone_global
    ollama_ok = verificar_ollama()
    status_txt = "Ollama OK" if ollama_ok else "Ollama OFFLINE"

    menu = pystray.Menu(
        pystray.MenuItem("Tecla IA", None, enabled=False),
        pystray.MenuItem(f"Atalho: {ATALHO.upper()}", None, enabled=False),
        pystray.MenuItem(f"Modelo: {MODELO_OLLAMA}", None, enabled=False),
        pystray.MenuItem(status_txt, None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Sair", _sair_bandeja),
    )

    icone_img = _criar_icone_imagem()
    _icone_global = pystray.Icon(
        "TeclaIA", icone_img,
        f"Tecla IA | {ATALHO.upper()} | {status_txt}",
        menu
    )
    _icone_global.run()


# ================================================================
#  MODO CONSOLE (fallback sem Pillow/pystray)
# ================================================================

def iniciar_modo_console():
    print()
    print("  [!] Modo console ativo (bandeja nao disponivel).")
    print("      Mantenha esta janela aberta. Para sair: Ctrl+C")
    print()
    print(f"  Aguardando {ATALHO.upper()} ...")
    print()
    try:
        keyboard.wait()
    except KeyboardInterrupt:
        print("\n  Tecla IA encerrado.")
        sys.exit(0)


# ================================================================
#  ENTRADA PRINCIPAL
# ================================================================

def main():
    print()
    print("==========================================")
    print("  TECLA IA - Expansor de Texto (Ollama)")
    print("==========================================")

    if verificar_ollama():
        print(f"  [OK] Ollama conectado — modelo: {MODELO_OLLAMA}")
    else:
        print("  [AVISO] Ollama nao detectado.")
        print("          Baixe em: https://ollama.com")
        print("          Rode:     ollama pull llama3.2")

    print(f"\n  Atalho ativo : {ATALHO.upper()}")
    print(f"  Visual       : janela de carregamento (canto inferior direito)")
    if TRAY_DISPONIVEL:
        print("  Bandeja      : icone AI perto do relogio")
    print()

    keyboard.add_hotkey(ATALHO, ao_pressionar_atalho, suppress=True)

    if TRAY_DISPONIVEL:
        iniciar_com_bandeja()
    else:
        iniciar_modo_console()


if __name__ == "__main__":
    main()
