# Diário de Bordo — Jogo da Cobrinha V2

Registro cronológico de **todas** as alterações feitas no projeto a partir do início da V2.
Cada entrada traz a data, o que foi feito, os arquivos afetados e o motivo da mudança.

## Como registrar

- Uma entrada por sessão de trabalho (ou por mudança relevante), **a mais recente no final**.
- Data e horário no formato `AAAA-MM-DD HH:MM` (horário de Brasília), no momento em que a mudança foi concluída.
- Descreva **o quê** mudou e **por quê**; o "como" detalhado fica no código e nos commits.
- Se a mudança corrige algo listado no [briefing_v2.md](briefing_v2.md), cite o item (ex.: `B3`, `J1`).

Modelo:

```markdown
### AAAA-MM-DD HH:MM — Título curto

**Feito:**
- ...

**Arquivos:** `caminho/arquivo.py`, ...

**Motivo / observações:** ...
```

---

## Entradas

### 2026-10-02 (horário não registrado) — Início da V2: diário de bordo e briefing

**Feito:**
- Criado este `LOG.md` como diário de bordo oficial da V2.
- Analisado o código da V1 (`Py_JogoDaCobrinha/Jogo da cobrinha/src/main.py`, 348 linhas), os 22 assets e o README.
- Criado o `briefing_v2.md` com o diagnóstico da V1 (bugs e limitações encontrados) e o plano de melhorias para estrutura do código, interface, jogabilidade e desempenho, organizado em fases.

**Arquivos:** `LOG.md` (novo), `briefing_v2.md` (novo).

> Horário não registrado: a regra de anotar horário começou depois desta entrada. Ela é anterior à das 08:48.

**Motivo / observações:**
- Nenhum arquivo da V1 foi alterado; ela segue como referência em `Py_JogoDaCobrinha/`.
- Estado do Git: a pasta `V2_JogoCobrinha/` é um repositório novo, ainda sem commits, e `Py_JogoDaCobrinha/` dentro dela é um repositório separado (histórico da V1). Como organizar isso está registrado como decisão em aberto no briefing (seção 8).

### 2026-10-02 08:48 — Decisões da V2 e criação do repositório

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

### 2026-10-02 08:58 — Licença MIT e Fase 0 (esqueleto do projeto)

**Feito:**
- **Licença:** `LICENSE` MIT, com o mesmo texto da V1 e copyright "2025-2026 João Vitor Fernandes".
- **Projeto (E7):** `pyproject.toml` com Python 3.11+, `pygame-ce>=2.5,<3`, extras `dev` (pytest, ruff), ponto de entrada `python -m cobrinha` / comando `cobrinha`, regras do ruff e configuração do pytest.
- **Configuração (E5):** `config.py` com grade (32 × 22, células de 25 px), HUD de 50 px, janela de 800 × 600 derivada da grade, FPS 60 e paleta de 16 cores.
- **Máquina de estados (E1, versão mínima):** `Jogo` com um único loop, pilha de estados (`trocar_estado`, `empilhar`, `desempilhar`) e `pygame.quit()` em um único ponto (`finally`). Fechar a janela ou apertar Esc encerra sem erro (B1, B5).
- **Domínio:** `dominio/grade.py` com `Posicao` em células (sem pygame).
- **Caminhos (E3):** `recursos.py` resolve `assets/` a partir do próprio pacote, independente da pasta de execução (B6). A fonte tem cache por tamanho e cai na fonte padrão do pygame enquanto a fonte pixel não existe.
- **Interface:** HUD (pontos, nível, recorde), campo em xadrez de grama pré-renderizado uma única vez (I5) e texto com cache (D3).
- **Testes:** 10 testes com pytest (grade, conversão célula → pixel, tamanho da janela, fechamento por QUIT e Esc, pilha de estados, cores do HUD e do xadrez). Rodam sem janela (driver `dummy`).
- **CI:** GitHub Actions com ruff (lint + formatação) e pytest no Ubuntu (Python 3.11, 3.12, 3.13) e no Windows (3.11).
- README atualizado: como executar, desenvolvimento, estrutura, selo do CI e licença.
- Briefing: a pasta `assets/` passou para dentro do pacote (`src/cobrinha/assets/`).

**Arquivos:** `LICENSE`, `pyproject.toml`, `src/cobrinha/__init__.py`, `src/cobrinha/__main__.py`, `src/cobrinha/config.py`, `src/cobrinha/jogo.py`, `src/cobrinha/recursos.py`, `src/cobrinha/dominio/__init__.py`, `src/cobrinha/dominio/grade.py`, `src/cobrinha/estados/__init__.py`, `src/cobrinha/estados/base.py`, `src/cobrinha/estados/jogando.py`, `src/cobrinha/ui/__init__.py`, `src/cobrinha/ui/campo.py`, `src/cobrinha/ui/hud.py`, `src/cobrinha/ui/texto.py`, `tests/conftest.py`, `tests/test_grade.py`, `tests/test_jogo.py`, `.github/workflows/ci.yml`, `README.md`, `briefing_v2.md`, `LOG.md` (todos novos, exceto os três últimos).

**Motivo / observações:**
- **Critério de pronto da Fase 0, verificado localmente (Python 3.11.8, pygame-ce 2.5.8):** `python -m cobrinha` abre a janela 800 × 600 com HUD e grade desenhados; o ruff passa sem apontamentos e os 10 testes passam.
- `assets/` fica dentro do pacote para funcionar tanto com `pip install` quanto com o PyInstaller (Fase 5).
- A partir daqui, **cada arquivo vai em um commit próprio** (regra nova do João). O commit anterior, `a49bde2`, tinha 4 arquivos porque foi feito antes da regra.
- Próximo passo: **Fase 1** (núcleo do jogo: cobra, comida, colisões e buffer de direção, com testes).

### 2026-10-02 09:07 — Fase 1 (núcleo do jogo) e actions do CI atualizadas

**Feito:**
- **CI:** `actions/checkout` v4 → v7 e `actions/setup-python` v5 → v7 (Node 24), eliminando o aviso de Node 20 obsoleto. Conferi as notas da v7: a única remoção é o input `pip-install`, que o workflow não usa.
- **Domínio (E2, E4), tudo sem pygame:**
  - `grade.py`: `Direcao` (Enum com deslocamento e `oposta`), `Posicao.vizinha` e `Grade` com dimensões injetáveis (os testes usam grades pequenas). `todas_as_posicoes()` virou `Grade.todas`.
  - `cobra.py`: corpo em `deque` + `set` de células ocupadas (D4), crescimento pendente, colisão que trata a cauda como livre quando a cobra não está crescendo, e **fila de direções com limite 2 (J1)**: cada comando é validado contra o último enfileirado. Isso corrige a meia-volta suicida (B3).
  - `comida.py`: sorteio direto entre as células livres, que devolve `None` com o campo cheio (B7, D5).
  - `partida.py`: **passo fixo** independente do FPS (D1), com teto de 3 passos por quadro para a cobra não "teleportar" após um travamento; colisões com parede e corpo; pontuação; vitória; eventos (`MOVEU`, `COMEU`, `BATEU`, `VENCEU`) para efeitos e sons futuros.
- **Telas:** `EstadoJogando` com partida real (setas **e** WASD) e novo `EstadoFimDePartida` sobre o campo congelado: derrota ou vitória, pontos, "NOVO RECORDE!", Enter/Espaço para jogar de novo e Esc para sair. O recorde vale para a sessão; a gravação em disco é da Fase 4 (J6).
- **Desenho provisório** (`ui/pecas.py`): cobra em blocos com listras e cabeça com olhos na direção do movimento; fruta vermelha com folha. Será trocado pela pixel art na Fase 3.
- **Depuração explícita (E8):** `python -m cobrinha --debug` mostra FPS e tamanho da cobra; `--semente N` repete a mesma sequência de comidas. `Jogo` ganhou `debug` e um `rng` único.
- **Testes:** de 10 para **49**. Novos: `test_cobra.py` (14), `test_comida.py` (3) e `test_partida.py` (16, incluindo 5 partidas aleatórias de 500 passos conferindo os invariantes a cada passo). `test_grade.py` e `test_jogo.py` foram ampliados (fluxo de fim de partida, WASD, argumentos).
- Briefing: J1 e a regra de vitória do J7 entraram na Fase 1; Fase 2 redefinida (pausa, níveis, 3-2-1 e menu simples); Fases 0 e 1 marcadas ✅. README com controles e opções de linha de comando.

**Arquivos:** `.github/workflows/ci.yml`, `src/cobrinha/config.py`, `src/cobrinha/dominio/grade.py`, `src/cobrinha/dominio/cobra.py` (novo), `src/cobrinha/dominio/comida.py` (novo), `src/cobrinha/dominio/partida.py` (novo), `src/cobrinha/ui/campo.py`, `src/cobrinha/ui/pecas.py` (novo), `src/cobrinha/jogo.py`, `src/cobrinha/estados/fim_de_partida.py` (novo), `src/cobrinha/estados/jogando.py`, `src/cobrinha/__main__.py`, `tests/test_grade.py`, `tests/test_cobra.py` (novo), `tests/test_comida.py` (novo), `tests/test_partida.py` (novo), `tests/test_jogo.py`, `briefing_v2.md`, `README.md`, `LOG.md`.

**Motivo / observações:**
- **Regra de vitória ajustada durante a implementação:** no passo em que a cobra come, a cauda ainda sai (o crescimento aparece no passo seguinte), então sempre sobra uma célula livre e "vitória quando não há célula livre" nunca dispararia. Agora a vitória é declarada quando o tamanho final da cobra (atual + crescimento pendente) preenche o campo. O `None` do sorteio continua como proteção contra laço infinito.
- **Bugs da V1 cobertos por testes:** B1 e B5 (saída limpa), B2 (cobra nasce alinhada à grade), B3 (curva rápida), B6 (caminhos, desde a Fase 0) e B7 (campo cheio). B4 (comando escondido) deixou de existir: virou o `--debug`; o atalho de nível volta como `--nivel` na Fase 2, quando existirem níveis.
- **Verificado localmente:** ruff sem apontamentos, 49 testes passando, jogo aberto de verdade com `--debug` e capturas de tela da partida e do fim de jogo conferidas.
- Próximo passo: **Fase 2** (pausa, níveis com progressão, contagem 3-2-1, menu inicial).
