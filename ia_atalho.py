#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TECLA IA - Expansor e Assistente de Texto com Ollama
=====================================================

Atalhos disponíveis:
  Ctrl+Alt+I  →  Reescreve em tom CASUAL (mensagens do dia a dia)
  Ctrl+Alt+O  →  Reescreve em tom FORMAL/PROFISSIONAL
  Ctrl+Alt+P  →  CORRIGE gramática e ortografia apenas
  Ctrl+Alt+R  →  RESPONDE ao texto como assistente IA

Como usar:
  1. Clique em qualquer campo de texto
  2. Digite seu texto ou pedido
  3. Pressione o atalho desejado
  4. Aguarde — o resultado aparece automaticamente!
"""

import keyboard
import pyperclip
import requests
import json
import time
import threading
import sys
import tkinter as tk

# ================================================================
#  CONFIGURAÇÕES GERAIS
# ================================================================

MODELO_OLLAMA = "llama3.2"
OLLAMA_URL    = "http://localhost:11434/api/generate"
TIMEOUT_API   = 60

# ================================================================
#  MODOS DE OPERAÇÃO
#  Cada atalho tem seu próprio comportamento, prompt e visual.
# ================================================================

MODOS = {
    "ctrl+alt+i": {
        "nome":       "Casual",
        "emoji":      "💬",
        "cor_fundo":  "#1e1e2e",
        "cor_titulo": "#89b4fa",   # azul
        "cor_ok":     "#89b4fa",
        "prompt_sistema": (
            "Voce e um assistente que reescreve mensagens curtas como se o USUARIO estivesse "
            "enviando para outra pessoa em tom casual e descontraido. "
            "Voce nunca responde ao texto — voce sempre o reescreve na VOZ de quem esta enviando.\n\n"
            "Regras:\n"
            "- Reescreva como mensagem casual que o usuario enviaria a um amigo ou colega\n"
            "- NUNCA responda ao texto, mesmo que seja uma pergunta\n"
            "- Se for pergunta, reescreva-a como pergunta que o usuario faz a alguem\n"
            "- Tom descontraido, amigavel, natural\n"
            "- Responda APENAS com o texto reescrito, sem aspas nem explicacoes"
        ),
        "prompt_usuario": (
            "Reescreva esta mensagem curta em tom casual, como se EU estivesse "
            "enviando para alguem. Nao responda, apenas reescreva: {texto}"
        ),
    },

    "ctrl+alt+o": {
        "nome":       "Formal",
        "emoji":      "👔",
        "cor_fundo":  "#1e2e1e",
        "cor_titulo": "#a6e3a1",   # verde
        "cor_ok":     "#a6e3a1",
        "prompt_sistema": (
            "Voce e um assistente que reescreve mensagens em tom formal e profissional, "
            "como se o USUARIO estivesse enviando para um cliente, chefe ou parceiro de negocios. "
            "Voce nunca responde ao texto — voce sempre o reescreve na VOZ de quem esta enviando.\n\n"
            "Regras:\n"
            "- Reescreva com linguagem formal, educada e profissional\n"
            "- NUNCA responda ao texto, mesmo que seja uma pergunta\n"
            "- Use expressoes como 'Prezado', 'Venho por meio deste', 'Atenciosamente' quando adequado\n"
            "- Mantenha o objetivo original da mensagem\n"
            "- Responda APENAS com o texto reescrito, sem aspas nem explicacoes"
        ),
        "prompt_usuario": (
            "Reescreva esta mensagem em tom formal e profissional, como se EU estivesse "
            "enviando para um cliente ou superior. Nao responda, apenas reescreva: {texto}"
        ),
    },

    "ctrl+alt+p": {
        "nome":       "Corrigir",
        "emoji":      "✏️",
        "cor_fundo":  "#2e1e1e",
        "cor_titulo": "#fab387",   # laranja
        "cor_ok":     "#fab387",
        "prompt_sistema": (
            "Voce e um revisor de texto especializado em portugues brasileiro. "
            "Sua unica funcao e corrigir erros de gramatica, ortografia, pontuacao e concordancia. "
            "Nao expanda, nao mude o tom, nao adicione frases — apenas corrija os erros.\n\n"
            "Regras:\n"
            "- Corrija apenas o que estiver errado gramaticalmente\n"
            "- Mantenha o tamanho e o estilo original do texto\n"
            "- Se o texto estiver correto, retorne-o sem alteracoes\n"
            "- Responda APENAS com o texto corrigido, sem aspas nem explicacoes"
        ),
        "prompt_usuario": (
            "Corrija os erros de gramatica e ortografia deste texto, sem alterar "
            "o estilo ou adicionar conteudo: {texto}"
        ),
    },

    "ctrl+alt+r": {
        "nome":       "Responder",
        "emoji":      "🤖",
        "cor_fundo":  "#1e1a2e",
        "cor_titulo": "#cba6f7",   # roxo
        "cor_ok":     "#cba6f7",
        "modo_resposta": True,     # substitui pelo resultado da IA diretamente
        "prompt_sistema": (
            "Voce e um assistente inteligente e direto ao ponto. "
            "Responda perguntas, execute pedidos, gere codigo, explique conceitos — "
            "qualquer tarefa que o usuario pedir.\n\n"
            "Regras:\n"
            "- Responda diretamente ao pedido do usuario\n"
            "- Para codigo, retorne apenas o codigo sem explicacoes longas\n"
            "- Para perguntas, seja claro e objetivo\n"
            "- Use portugues brasileiro\n"
            "- Nao adicione prefixos como 'Claro!', 'Com certeza!', 'Aqui esta:' — va direto ao ponto"
        ),
        "prompt_usuario": "{texto}",
    },
}

# ================================================================
#  JANELA DE CARREGAMENTO
# ================================================================

class JanelaCarregando:
    """
    Popup no canto inferior direito com preview de streaming em tempo real.
    O texto da IA vai aparecendo à medida que é gerado — como o ChatGPT.
    """
    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self):
        self._root        = None
        self._lbl_spinner = None
        self._lbl_titulo  = None
        self._txt_stream  = None   # widget Text para o preview do streaming
        self._spinner_idx = 0
        self._animando    = False
        self._cor_titulo  = "#89b4fa"
        self._cor_fundo   = "#1e1e2e"
        self._cor_borda   = "#313244"
        self._cor_texto   = "#cdd6f4"
        # Buffer de streaming — atualizado pela thread Ollama, lido pela thread tkinter
        self._stream_buf  = ""
        self._stream_lock = threading.Lock()

    # ── Ciclo de vida ──────────────────────────────────────────────

    def mostrar(self, titulo, mensagem="", cor_fundo="#1e1e2e", cor_titulo="#89b4fa"):
        self._cor_fundo  = cor_fundo
        self._cor_titulo = cor_titulo
        with self._stream_lock:
            self._stream_buf = mensagem
        threading.Thread(
            target=self._criar_janela, args=(titulo,), daemon=True
        ).start()
        time.sleep(0.25)

    def push_stream(self, chunk: str):
        """Chamado pela thread de streaming a cada novo token recebido."""
        with self._stream_lock:
            self._stream_buf += chunk

    def fechar(self, titulo_final=None, cor=None, delay=1.8):
        try:
            _cor = cor or self._cor_titulo
            if titulo_final and self._lbl_titulo:
                self._lbl_titulo.config(text=titulo_final, fg=_cor)
            if self._lbl_spinner:
                icone = "✗" if cor == "#f38ba8" else "✓"
                self._lbl_spinner.config(text=icone, fg=_cor)
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

    def _criar_janela(self, titulo):
        self._root = tk.Tk()
        root = self._root
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-alpha", 0.95)
        root.configure(bg=self._cor_fundo)

        # Janela maior para mostrar o preview do texto gerado
        largura, altura = 380, 160
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        root.geometry(f"{largura}x{altura}+{sw - largura - 20}+{sh - altura - 60}")

        frame = tk.Frame(root, bg=self._cor_borda, padx=1, pady=1)
        frame.pack(fill="both", expand=True)
        inner = tk.Frame(frame, bg=self._cor_fundo, padx=12, pady=8)
        inner.pack(fill="both", expand=True)

        # Linha do topo: spinner + título
        linha1 = tk.Frame(inner, bg=self._cor_fundo)
        linha1.pack(fill="x", pady=(0, 6))

        self._lbl_spinner = tk.Label(
            linha1, text=self.SPINNER_FRAMES[0],
            bg=self._cor_fundo, fg=self._cor_titulo,
            font=("Segoe UI", 13)
        )
        self._lbl_spinner.pack(side="left", padx=(0, 8))

        self._lbl_titulo = tk.Label(
            linha1, text=titulo,
            bg=self._cor_fundo, fg=self._cor_titulo,
            font=("Segoe UI", 10, "bold"), anchor="w"
        )
        self._lbl_titulo.pack(side="left", fill="x", expand=True)

        # Área de texto com o preview do streaming
        self._txt_stream = tk.Text(
            inner,
            bg="#181825", fg=self._cor_texto,
            font=("Segoe UI", 9),
            relief="flat", bd=0,
            wrap="word",
            height=5,
            state="disabled",
            cursor="arrow",
        )
        self._txt_stream.pack(fill="both", expand=True)

        # Escreve mensagem inicial
        with self._stream_lock:
            buf = self._stream_buf
        self._escrever_texto(buf)

        self._animando = True
        self._loop_atualizacao()
        root.mainloop()

    def _escrever_texto(self, texto):
        """Substitui todo o conteúdo da área de texto."""
        try:
            self._txt_stream.config(state="normal")
            self._txt_stream.delete("1.0", "end")
            self._txt_stream.insert("end", texto)
            self._txt_stream.see("end")           # rola para o fim (efeito typewriter)
            self._txt_stream.config(state="disabled")
        except Exception:
            pass

    def _loop_atualizacao(self):
        """
        Roda na thread tkinter (via after).
        Atualiza o spinner e o preview de streaming a cada 80ms.
        """
        if not self._animando or not self._root:
            return
        try:
            # Spinner
            self._spinner_idx = (self._spinner_idx + 1) % len(self.SPINNER_FRAMES)
            self._lbl_spinner.config(text=self.SPINNER_FRAMES[self._spinner_idx])

            # Preview do streaming — lê o buffer de forma thread-safe
            with self._stream_lock:
                buf = self._stream_buf
            self._escrever_texto(buf)

            self._root.after(80, self._loop_atualizacao)
        except Exception:
            pass


_janela      = JanelaCarregando()
_processando = False

# ================================================================
#  COMUNICAÇÃO COM OLLAMA
# ================================================================

def verificar_ollama():
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def chamar_ollama_stream(prompt_sistema, prompt_usuario, on_chunk):
    """
    Chama o Ollama em modo streaming.
    on_chunk(texto: str) é chamado a cada novo trecho recebido.
    Retorna (sucesso: bool, texto_completo: str).
    """
    try:
        payload = {
            "model":   MODELO_OLLAMA,
            "prompt":  prompt_usuario,
            "system":  prompt_sistema,
            "stream":  True,                        # ← streaming ativado
            "options": {"temperature": 0.7, "num_predict": 500},
        }
        resp = requests.post(
            OLLAMA_URL, json=payload,
            timeout=TIMEOUT_API, stream=True
        )
        resp.raise_for_status()

        texto_completo = ""
        for linha in resp.iter_lines():
            if not linha:
                continue
            try:
                data  = json.loads(linha)
                chunk = data.get("response", "")
                if chunk:
                    texto_completo += chunk
                    on_chunk(chunk)              # ← notifica a janela em tempo real
                if data.get("done", False):
                    break
            except json.JSONDecodeError:
                continue

        return (True, texto_completo.strip()) if texto_completo.strip() \
               else (False, "Resposta vazia do modelo.")

    except requests.ConnectionError:
        return False, "Ollama nao esta rodando. Inicie o Ollama primeiro."
    except requests.Timeout:
        return False, "Tempo limite excedido. Modelo pode estar lento."
    except Exception as e:
        return False, f"Erro: {e}"


# ================================================================
#  HISTÓRICO PARA DESFAZER (Ctrl+Alt+Z)
# ================================================================

_historico = {
    "texto_original":  "",   # texto antes da expansão
    "texto_expandido": "",   # texto depois da expansão
    "disponivel":      False,
}


# ================================================================
#  HELPERS DE TECLADO
# ================================================================

def _liberar_modificadores():
    """
    Libera Ctrl, Alt e Shift após operações com keyboard.send().
    Sem isso, as teclas ficam "presas" no hook e a digitação trava.
    """
    for tecla in ("ctrl", "alt", "shift"):
        try:
            keyboard.release(tecla)
        except Exception:
            pass
    time.sleep(0.05)


def _colar_texto(texto: str):
    """Seleciona tudo no campo atual e substitui pelo texto fornecido."""
    pyperclip.copy(texto)
    time.sleep(0.1)
    keyboard.send("ctrl+a")
    time.sleep(0.15)
    keyboard.send("ctrl+v")
    time.sleep(0.1)
    _liberar_modificadores()   # ← solta Ctrl/Alt para não travar o teclado


# ================================================================
#  LÓGICA DE EXECUÇÃO
# ================================================================

def ao_pressionar(atalho):
    """Fábrica de callbacks — cria um handler para cada atalho."""
    def _handler():
        global _processando
        if _processando:
            return
        _processando = True
        # Libera os modificadores do atalho que acabou de disparar
        # antes de iniciar a thread, para evitar estado residual
        _liberar_modificadores()
        threading.Thread(target=_executar, args=(atalho,), daemon=True).start()
    return _handler


def _executar(atalho):
    global _processando, _historico
    modo = MODOS[atalho]

    try:
        # 1. Captura o texto do campo
        clip_original = pyperclip.paste()
        pyperclip.copy("")
        time.sleep(0.15)
        keyboard.send("ctrl+a")
        time.sleep(0.2)
        keyboard.send("ctrl+c")
        time.sleep(0.4)
        _liberar_modificadores()

        texto = pyperclip.paste().strip()

        if not texto or len(texto) < 2:
            pyperclip.copy(clip_original)
            _janela.mostrar(
                f"{modo['emoji']}  Nada encontrado",
                "Clique no campo de texto e tente novamente.",
                cor_fundo=modo["cor_fundo"],
                cor_titulo=modo["cor_titulo"]
            )
            _janela.fechar(titulo_final="✗  Nada encontrado", cor="#f38ba8", delay=2)
            return

        preview = f'"{texto[:50]}..."' if len(texto) > 50 else f'"{texto}"'

        # 2. Abre a janela com preview de streaming
        _janela.mostrar(
            titulo=f"{modo['emoji']}  Tecla IA — {modo['nome']}",
            mensagem=preview,
            cor_fundo=modo["cor_fundo"],
            cor_titulo=modo["cor_titulo"]
        )

        # 3. Chama Ollama com streaming
        prompt_usuario = modo["prompt_usuario"].format(texto=texto)
        sucesso, resultado = chamar_ollama_stream(
            modo["prompt_sistema"],
            prompt_usuario,
            on_chunk=_janela.push_stream
        )

        if sucesso:
            # 4. Salva no histórico para o desfazer
            _historico["texto_original"]  = texto
            _historico["texto_expandido"] = resultado
            _historico["disponivel"]      = True

            # 5. Cola o resultado no campo
            _colar_texto(resultado)

            _janela.fechar(
                titulo_final=f"✓  {modo['nome']} — Pronto!  (Ctrl+Alt+Z desfaz)",
                cor=modo["cor_ok"],
                delay=2.5
            )
            print(f"  [{modo['nome'].upper()}] {resultado[:80]}...")
        else:
            _liberar_modificadores()
            _janela.fechar(
                titulo_final=f"✗  {resultado[:55]}",
                cor="#f38ba8",
                delay=3
            )
            print(f"  [ERRO] {resultado}")

        time.sleep(2)
        pyperclip.copy(clip_original)

    except Exception as e:
        _liberar_modificadores()
        _janela.fechar(titulo_final="✗  Erro inesperado", cor="#f38ba8", delay=3)
        print(f"  [ERRO] {e}")
    finally:
        _processando = False


def _desfazer():
    """Ctrl+Alt+Z — restaura o texto original antes da última expansão."""
    global _historico
    if not _historico["disponivel"]:
        _janela.mostrar(
            "↩  Nada para desfazer",
            "Nenhuma expansao recente encontrada.",
            cor_fundo="#2e1e2e",
            cor_titulo="#f38ba8"
        )
        _janela.fechar(titulo_final="✗  Nada para desfazer", cor="#f38ba8", delay=2)
        return

    _liberar_modificadores()
    _colar_texto(_historico["texto_original"])
    _historico["disponivel"] = False

    _janela.mostrar(
        "↩  Desfeito!",
        f'Restaurado: "{_historico["texto_original"][:60]}"',
        cor_fundo="#1e2e1e",
        cor_titulo="#a6e3a1"
    )
    _janela.fechar(titulo_final="✓  Texto original restaurado", cor="#a6e3a1", delay=2)
    print("  [DESFAZER] Texto original restaurado.")


# ================================================================
#  BANDEJA DO SISTEMA (opcional)
# ================================================================

try:
    from PIL import Image, ImageDraw, ImageFont
    import pystray
    TRAY_DISPONIVEL = True
except ImportError:
    TRAY_DISPONIVEL = False

_icone_global = None


def _criar_icone_imagem():
    size = 64
    img  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
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
    draw.text((size // 2, size // 2), "AI", fill=(255, 255, 255, 255), font=font, anchor="mm")
    return img


def _sair(icon, _item):
    icon.stop()
    sys.exit(0)


def iniciar_com_bandeja():
    global _icone_global
    ollama_ok  = verificar_ollama()
    status_txt = "Ollama OK" if ollama_ok else "Ollama OFFLINE"

    menu = pystray.Menu(
        pystray.MenuItem("Tecla IA", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Ctrl+Alt+I  →  Casual",   None, enabled=False),
        pystray.MenuItem("Ctrl+Alt+O  →  Formal",   None, enabled=False),
        pystray.MenuItem("Ctrl+Alt+P  →  Corrigir", None, enabled=False),
        pystray.MenuItem("Ctrl+Alt+R  →  Responder",None, enabled=False),
        pystray.MenuItem("Ctrl+Alt+Z  →  Desfazer", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(status_txt, None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Sair", _sair),
    )

    _icone_global = pystray.Icon(
        "TeclaIA", _criar_icone_imagem(),
        f"Tecla IA | {status_txt}", menu
    )
    _icone_global.run()


# ================================================================
#  MODO CONSOLE (fallback)
# ================================================================

def iniciar_modo_console():
    print()
    print("  Modo console — mantenha esta janela aberta. Ctrl+C para sair.")
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
    print("  TECLA IA — Assistente de Texto (Ollama)")
    print("==========================================")
    print()

    if verificar_ollama():
        print(f"  [OK] Ollama conectado — modelo: {MODELO_OLLAMA}")
    else:
        print("  [AVISO] Ollama nao detectado.")
        print("          Baixe em: https://ollama.com")
        print("          Rode:     ollama pull llama3.2")

    print()
    print("  Atalhos ativos:")
    print("    Ctrl+Alt+I  →  💬 Casual     (reescreve em tom do dia a dia)")
    print("    Ctrl+Alt+O  →  👔 Formal     (reescreve em tom profissional)")
    print("    Ctrl+Alt+P  →  ✏️  Corrigir   (corrige gramática e ortografia)")
    print("    Ctrl+Alt+R  →  🤖 Responder  (a IA responde/executa seu pedido)")
    print("    Ctrl+Alt+Z  →  ↩  Desfazer   (restaura o texto anterior)")
    print()

    # Registra os 4 modos de expansão
    for atalho in MODOS:
        keyboard.add_hotkey(atalho, ao_pressionar(atalho), suppress=True)

    # Registra o desfazer
    keyboard.add_hotkey("ctrl+alt+z", _desfazer, suppress=True)

    if TRAY_DISPONIVEL:
        iniciar_com_bandeja()
    else:
        iniciar_modo_console()


if __name__ == "__main__":
    main()
