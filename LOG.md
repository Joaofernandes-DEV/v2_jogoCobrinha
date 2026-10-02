# Diário de Bordo — Jogo da Cobrinha V2

Registro cronológico de **todas** as alterações feitas no projeto a partir do início da V2.
Cada entrada traz a data, o que foi feito, os arquivos afetados e o motivo da mudança.

## Como registrar

- Uma entrada por sessão de trabalho (ou por mudança relevante), **a mais recente no final**.
- Data no formato `AAAA-MM-DD`.
- Descreva **o quê** mudou e **por quê**; o "como" detalhado fica no código e nos commits.
- Se a mudança corrige algo listado no [briefing_v2.md](briefing_v2.md), cite o item (ex.: `B3`, `J1`).

Modelo:

```markdown
### AAAA-MM-DD — Título curto

**Feito:**
- ...

**Arquivos:** `caminho/arquivo.py`, ...

**Motivo / observações:** ...
```

---

## Entradas

### 2026-10-02 — Início da V2: diário de bordo e briefing

**Feito:**
- Criado este `LOG.md` como diário de bordo oficial da V2.
- Analisado o código da V1 (`Py_JogoDaCobrinha/Jogo da cobrinha/src/main.py`, 348 linhas), os 22 assets e o README.
- Criado o `briefing_v2.md` com o diagnóstico da V1 (bugs e limitações encontrados) e o plano de melhorias para estrutura do código, interface, jogabilidade e desempenho, organizado em fases.

**Arquivos:** `LOG.md` (novo), `briefing_v2.md` (novo).

**Motivo / observações:**
- Nenhum arquivo da V1 foi alterado; ela segue como referência em `Py_JogoDaCobrinha/`.
- Estado do Git: a pasta `V2_JogoCobrinha/` é um repositório novo, ainda sem commits, e `Py_JogoDaCobrinha/` dentro dela é um repositório separado (histórico da V1). Como organizar isso está registrado como decisão em aberto no briefing (seção 8).

### 2026-10-02 — Decisões da V2 e criação do repositório

**Feito:**
- Fechadas as 5 decisões do briefing. A seção 8 virou "Decisões tomadas":
  1. Repositório novo para a V2 (`Joaofernandes-DEV/v2_jogoCobrinha`); a V1 fica local, só como referência, e está no `.gitignore`.
  2. Grade com células de 25 px: 32 × 22 células + HUD de 50 px, em janela 800 × 600.
  3. Arte refeita do zero em pixel art (sprites 25 × 25 nativos, paleta de até 16 cores, fonte pixel livre).
  4. Escopo de conteúdo da V2 definido. Entram 3 níveis com obstáculos, fruta dourada, top 5 de recordes, modos Clássico e Sem bordas, sons, opções, CI e executável. Remapeamento de teclas, power-ups extras, ranking online, partículas e movimento interpolado vão para o backlog da V3.
  5. Python 3.11+ com `pygame-ce`.
- Seções 1, 3, 4, 6, 7 e 9 do briefing ajustadas a essas decisões. O roteiro foi reescrito considerando que a V2 é uma reescrita do zero.
- Criados `.gitignore` e `README.md` inicial.
- Inicializado o repositório Git na pasta da V2, com o primeiro commit e push para `main` no GitHub.

**Arquivos:** `briefing_v2.md`, `LOG.md`, `.gitignore` (novo), `README.md` (novo).

**Motivo / observações:**
- Antes, a pasta não tinha repositório próprio. O Git que aparecia era o da pasta de usuário (`C:\Users\joaov`). Foi criado um `git init` dedicado em `V2_JogoCobrinha/`.
- Ainda não há `LICENSE`. A V1 usa MIT; definir se a V2 segue igual.
