# Tecla IA — Expansor Inteligente de Texto para Windows

> Pressione um atalho e sua ideia vira uma mensagem completa — tudo rodando localmente, sem custo e sem enviar dados para a nuvem.

---

## O que é o Tecla IA?

O Tecla IA é um programa leve que roda em segundo plano no Windows. Com um simples atalho de teclado (**Ctrl+Alt+I**), ele captura o texto que você digitou em qualquer campo, envia para uma IA rodando localmente no seu computador e substitui o texto automaticamente por uma versão mais completa e natural.

Tudo acontece localmente: nenhum dado sai da sua máquina, sem mensalidade, sem limite de uso.

---

## Como funciona

1. Você digita uma ideia curta em qualquer campo de texto
2. Pressiona **Ctrl+Alt+I**
3. Uma janela de carregamento aparece no canto inferior direito
4. O texto é substituído automaticamente pela versão expandida

A IA sempre reescreve o texto **na sua voz**, como se você estivesse enviando uma mensagem para outra pessoa. Ela nunca responde ao texto — apenas o expande.

### Exemplos

| Você digita | Tecla IA reescreve como |
|---|---|
| `Bom dia` | Olá, bom dia! Tudo bem contigo? |
| `Você está aí?` | Oi! Por acaso você está aí agora? |
| `Reunião amanhã` | Oi! Passando para confirmar nossa reunião amanhã, tudo certo? |
| `Obrigado pela ajuda` | Muito obrigado pela sua ajuda, foi essencial! |
| `Preciso de um favor` | Olá! Precisaria de um pequeno favor seu, pode me ajudar? |

---

## A ideia por trás do projeto

A ideia surgiu da necessidade de digitar mensagens mais completas e naturais sem perder tempo elaborando cada frase. Em vez de digitar um texto longo, o usuário digita apenas a essência da mensagem e deixa a IA completar.

Três princípios guiaram o projeto:

- **Privacidade total** — a IA roda 100% local, nenhum dado sai do computador
- **Zero custo de uso** — sem API paga, sem limite de mensagens, sem assinatura
- **Funciona em qualquer lugar** — Word, Outlook, WhatsApp Web, navegador, Notepad, Discord e qualquer app Windows com campo de texto

---

## Requisitos

| Componente | Descrição |
|---|---|
| Windows 10 / 11 | Sistema operacional |
| Python 3.10+ | Linguagem do projeto — [python.org](https://www.python.org/downloads/) |
| Ollama | Motor de IA local — [ollama.com](https://ollama.com) |
| Modelo llama3.2 | ~2 GB — instalado via `ollama pull llama3.2` |
| RAM | 8 GB mínimo, 16 GB recomendado |

---

## Instalação

### 1. Instalar o Python

Baixe em [python.org](https://www.python.org/downloads/).
Durante a instalação, marque obrigatoriamente **"Add Python to PATH"**.

### 2. Instalar o Ollama

Baixe em [ollama.com](https://ollama.com), instale e execute no terminal:

```bash
ollama pull llama3.2
```

Aguarde o download do modelo (~2 GB).

### 3. Instalar as dependências do Tecla IA

Clique duas vezes em:

```
1_INSTALAR.bat
```

### 4. Iniciar

Clique duas vezes em:

```
2_INICIAR_COMO_ADMIN.bat
```

Aceite a janela de permissão de Administrador — necessária para capturar teclas globalmente.

### 5. (Opcional) Iniciar com o Windows

```
3_INICIAR_COM_WINDOWS.bat
```

---

## Estrutura de arquivos

```
TeclaIA/
├── ia_atalho.py              # Código principal
├── requirements.txt          # Dependências Python
├── 1_INSTALAR.bat            # Instala as dependências
├── 2_INICIAR_COMO_ADMIN.bat  # Inicia o programa
├── 3_INICIAR_COM_WINDOWS.bat # Configura início automático
└── README.md                 # Este arquivo
```

---

## Personalização

Abra `ia_atalho.py` em qualquer editor de texto e edite a seção `CONFIGURACOES` no topo:

```python
ATALHO        = "ctrl+alt+i"   # Mude o atalho de teclado
MODELO_OLLAMA = "llama3.2"     # Mude o modelo de IA
TIMEOUT_API   = 60             # Tempo máximo de espera (segundos)
```

### Outros modelos disponíveis no Ollama

| Modelo | Característica |
|---|---|
| `llama3.2` | Padrão — bom equilíbrio velocidade/qualidade |
| `llama3.2:1b` | Mais rápido, ideal para PCs com menos RAM |
| `mistral` | Boa alternativa, respostas mais criativas |
| `phi3` | Modelo leve da Microsoft |

Para baixar outro modelo: `ollama pull <nome>`

---

## Solução de problemas

**O atalho não funciona**
Verifique se `2_INICIAR_COMO_ADMIN.bat` foi executado como Administrador.

**Ollama não detectado**
Abra o Ollama pela bandeja do sistema ou reinicie o computador. Verifique em `http://localhost:11434`.

**Texto não é substituído em algum app**
Alguns apps bloqueiam Ctrl+A. Nesse caso, selecione o texto manualmente antes de pressionar o atalho.

**Resposta muito lenta**
Troque o modelo para `llama3.2:1b` (mais leve) ou feche outros programas pesados.

**Erro de tempo limite**
Aumente `TIMEOUT_API` no arquivo `ia_atalho.py` (padrão: 60 segundos).

---

## Tecnologias

- [Python 3](https://www.python.org/) — linguagem principal
- [keyboard](https://github.com/boppreh/keyboard) — captura de atalhos globais
- [pyperclip](https://github.com/asweigart/pyperclip) — leitura/escrita na área de transferência
- [requests](https://requests.readthedocs.io/) — comunicação com a API local do Ollama
- [tkinter](https://docs.python.org/3/library/tkinter.html) — janela de carregamento visual (incluso no Python)
- [Ollama](https://ollama.com) — motor de execução de modelos de IA localmente
- [llama3.2](https://ollama.com/library/llama3.2) (Meta) — modelo de linguagem
