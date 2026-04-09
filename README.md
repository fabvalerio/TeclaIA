# Tecla IA — Assistente de texto local para Windows

> Atalhos globais transformam ou corrigem o que você digitou usando o Ollama no seu PC — sem nuvem, sem custo por uso.

---

## O que é o Tecla IA?

Programa leve que fica em segundo plano no Windows. Em qualquer campo de texto, você usa um atalho; o texto selecionado (ou o campo atual) é enviado à API local do **Ollama** e o resultado substitui o texto automaticamente.

- **Privacidade** — inferência só na máquina (Ollama em `localhost`)
- **Sem assinatura** — não depende de API paga
- **Uso amplo** — funciona na maioria dos apps com campo de texto (Word, navegador, WhatsApp Web, e-mail, etc.)

Enquanto a IA gera, uma janela no canto inferior direito mostra **pré-visualização em streaming** do texto, no estilo “vai aparecendo aos poucos”.

Se **Pillow** e **pystray** estiverem instalados, um ícone **AI** aparece na bandeja do sistema com o menu de atalhos e a opção **Sair**. Caso contrário, o programa segue funcionando em modo console (janela do CMD aberta).

---

## Atalhos

| Atalho | Modo | Comportamento |
|--------|------|----------------|
| **Ctrl+Alt+I** | Casual | Reescreve na sua voz, tom descontraído (mensagem para outra pessoa). Não “responde” ao texto — só reformula. |
| **Ctrl+Alt+O** | Formal | Reescreve em tom profissional (cliente, chefe, e-mail formal). Mesma regra: é a sua mensagem, não uma resposta da IA ao conteúdo. |
| **Ctrl+Alt+P** | Corrigir | Apenas gramática, ortografia e pontuação em português; não expande nem muda o tom. |
| **Ctrl+Alt+R** | Responder | A IA **responde de fato** ao que você escreveu (perguntas, pedidos, código, explicações). |
| **Ctrl+Alt+Z** | Desfazer | Restaura o texto **antes** da última operação feita com I, O, P ou R (um nível). |

---

## Como usar (resumo)

1. Clique no campo de texto e digite (ou selecione o trecho desejado).
2. Pressione o atalho do modo que quer (**I**, **O**, **P** ou **R**).
3. Aguarde a janela de progresso e o fim da geração; o texto é colado no lugar.
4. Se quiser voltar atrás, use **Ctrl+Alt+Z** logo em seguida.

### Exemplos (modos Casual / Formal)

| Você digita | Ideia do resultado |
|-------------|-------------------|
| `Bom dia` | Saudação mais completa e natural |
| `Reunião amanhã` | Mensagem confirmando ou lembrando a reunião |
| `Obrigado pela ajuda` | Agradecimento mais elaborado |

*(O resultado exato depende do modelo e do prompt configurados em `ia_atalho.py`.)*

---

## Requisitos

| Componente | Descrição |
|------------|-----------|
| Windows 10 / 11 | Sistema operacional |
| Python 3.10+ | [python.org](https://www.python.org/downloads/) — marque **Add Python to PATH** |
| Ollama | [ollama.com](https://ollama.com) |
| Modelo sugerido | `llama3.2` (~2 GB) — `ollama pull llama3.2` |
| RAM | 8 GB mínimo; 16 GB recomendado |

---

## Instalação

### 1. Python e Ollama

Instale o Python e o Ollama pelos sites oficiais. Depois, no terminal:

```bash
ollama pull llama3.2
```

### 2. Dependências do projeto

Execute (duplo clique):

```
1_INSTALAR.bat
```

Isso instala `keyboard`, `pyperclip` e `requests`, e tenta instalar **pystray** e **Pillow** para o ícone na bandeja (se falhar, o app continua sem bandeja).

### 3. Iniciar

Execute como administrador (duplo clique):

```
2_INICIAR_COMO_ADMIN.bat
```

A elevação é necessária para **atalhos globais** em qualquer aplicativo.

### 4. (Opcional) Início com o Windows

```
3_INICIAR_COM_WINDOWS.bat
```

### 5. (Opcional) Gerar `TeclaIA.exe`

```
4_CRIAR_EXE.bat
```

Gera `dist\TeclaIA.exe` com PyInstaller (`--onefile`, sem console, com UAC admin). Quem usar o `.exe` ainda precisa do **Ollama** instalado e do modelo baixado.

---

## Estrutura de arquivos

```
TeclaIA/
├── ia_atalho.py              # Código principal (MODOS, Ollama, bandeja, atalhos)
├── requirements.txt          # Versões fixas das dependências principais
├── ia_atalho.spec            # Especificação PyInstaller (alternativa ao fluxo do .bat)
├── 1_INSTALAR.bat            # pip install das dependências
├── 2_INICIAR_COMO_ADMIN.bat  # Inicia o programa
├── 3_INICIAR_COM_WINDOWS.bat # Atalho na pasta Inicializar do Windows
├── 4_CRIAR_EXE.bat           # Build do executável com PyInstaller
├── LEIAME.txt                # Guia rápido em texto puro (parcialmente legado)
├── .gitignore
└── README.md                 # Este arquivo
```

---

## Personalização

Edite o topo de `ia_atalho.py`:

- **`MODELO_OLLAMA`** — nome do modelo no Ollama (ex.: `llama3.2`, `llama3.2:1b`, `mistral`).
- **`OLLAMA_URL`** — endpoint da API generate (padrão: `http://localhost:11434/api/generate`).
- **`TIMEOUT_API`** — tempo máximo da requisição em segundos (padrão: 60).
- **`MODOS`** — dicionário por atalho (`ctrl+alt+i`, etc.): nomes, cores da janela, `prompt_sistema`, `prompt_usuario` e `modo_resposta` (apenas em **Responder**).

Para mudar atalhos, altere as chaves em `MODOS` e o registro em `main()` (e o menu da bandeja, se quiser manter os textos alinhados).

---

## Solução de problemas

**Atalho não funciona**  
Confirme que o programa foi iniciado com **administrador** (`2_INICIAR_COMO_ADMIN.bat` ou `TeclaIA.exe` aceitando o UAC).

**Ollama não detectado**  
Abra o Ollama pela bandeja ou reinicie o PC. Teste: [http://localhost:11434](http://localhost:11434).

**Texto não substitui em algum app**  
Alguns programas bloqueiam “selecionar tudo”. Selecione o texto manualmente antes do atalho.

**Resposta lenta**  
Use um modelo menor (`llama3.2:1b`) ou feche apps pesados.

**Timeout**  
Aumente `TIMEOUT_API` em `ia_atalho.py`.

**Sem ícone na bandeja**  
Normal se `pystray`/`Pillow` não instalaram; use o console aberto ou reinstale com `pip install pystray Pillow` (wheel compatível com seu Python).

---

## Tecnologias

- [Python 3](https://www.python.org/)
- [keyboard](https://github.com/boppreh/keyboard) — atalhos globais
- [pyperclip](https://github.com/asweigart/pyperclip) — área de transferência
- [requests](https://requests.readthedocs.io/) — HTTP para o Ollama
- [tkinter](https://docs.python.org/3/library/tkinter.html) — janela de carregamento / streaming
- [Pillow](https://python-pillow.org/) + [pystray](https://github.com/moses-palmer/pystray) — ícone na bandeja (opcional)
- [PyInstaller](https://pyinstaller.org/) — build do `.exe` (via `4_CRIAR_EXE.bat`)
- [Ollama](https://ollama.com) — execução local de modelos

Dependências pinadas em `requirements.txt`:

- `keyboard==0.13.5`
- `pyperclip==1.9.0`
- `requests==2.32.3`
