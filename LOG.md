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

### 2026-10-02 09:21 — Fase 2 (fluxo da partida: menu, níveis, pausa e contagem)

**Feito:**
- **Níveis como dados (J3):** `dominio/niveis.py` com 3 níveis: velocidade de 8, 11 e 14 passos/s e metas de 10, 12 e 15 comidas. A velocidade saiu do `config.py` e passou a ser do nível.
- **Progressão sem interrupção (J3):** a `Partida` passou a representar um nível. Ao bater a meta, a situação vira `NIVEL_CONCLUIDO` e `proxima_fase()` cria o nível seguinte levando os pontos (a cobra recomeça com 3). Bater a meta do último nível é vitória. A pergunta Y/N no meio do jogo, da V1, deixou de existir.
- **Progresso da sessão:** `dominio/progresso.py` guarda o recorde e o maior nível liberado. Ainda não é gravado em disco (J6, Fase 4).
- **Telas novas:**
  - **Menu principal:** Jogar, Nível inicial (← → circula só entre os níveis liberados) e Sair.
  - **Contagem 3-2-1 (J10):** antes de cada nível e ao sair da pausa; Enter pula.
  - **Pausa (J2):** Esc ou P. Opções: Continuar, Reiniciar, Menu principal e Sair. Também pausa sozinho quando a janela perde o foco, inclusive durante a contagem.
  - **Nível concluído:** mostra pontos, a meta do próximo nível e as opções Próximo nível e Menu.
- **Fim de partida** agora com menu: Jogar de novo (a partir do nível em que a campanha começou), Menu principal e Sair. Sair de uma partida pela pausa também conta para o recorde.
- **Navegação centralizada:** `estados/navegacao.py` concentra todas as trocas de tela, com o diagrama do fluxo no topo, e evita importações circulares entre as telas.
- **Componentes de UI:** `ui/menu.py` (menu navegável por setas/WASD, Enter, e ← → para itens ajustáveis) e `ui/painel.py` (véu escuro e textos centralizados).
- **HUD:** mostra o progresso da meta (`NÍVEL 1   4/10`).
- **`--nivel N` (E8):** pula o menu e começa no nível N, que é liberado. Fecha a pendência do antigo comando escondido (B4).
- **Testes:** de 49 para **82**. Novos: `test_estados.py` (17, fluxo completo entre telas), `test_menu.py` (6), `test_niveis.py` (5) e +5 em `test_partida.py` (meta, último nível, próxima fase). O `conftest.py` limpa os caches de fonte e texto depois de cada teste.

**Arquivos:** `src/cobrinha/config.py`, `src/cobrinha/dominio/niveis.py` (novo), `src/cobrinha/dominio/progresso.py` (novo), `src/cobrinha/dominio/partida.py`, `src/cobrinha/jogo.py`, `src/cobrinha/ui/texto.py`, `src/cobrinha/ui/hud.py`, `src/cobrinha/ui/painel.py` (novo), `src/cobrinha/ui/menu.py` (novo), `src/cobrinha/estados/navegacao.py` (novo), `src/cobrinha/estados/jogando.py`, `src/cobrinha/estados/contagem.py` (novo), `src/cobrinha/estados/pausa.py` (novo), `src/cobrinha/estados/nivel_concluido.py` (novo), `src/cobrinha/estados/fim_de_partida.py`, `src/cobrinha/estados/menu_principal.py` (novo), `src/cobrinha/__main__.py`, `tests/conftest.py`, `tests/test_partida.py`, `tests/test_niveis.py` (novo), `tests/test_menu.py` (novo), `tests/test_estados.py` (novo), `tests/test_jogo.py`, `briefing_v2.md`, `README.md`, `LOG.md`.

**Motivo / observações:**
- **Problemas visuais achados nas capturas e corrigidos:**
  1. O marcador de seleção em texto (`> … <`) se misturava com as setas do seletor de nível. Virou dois triângulos desenhados.
  2. Itens com maiúscula acentuada (Í, Ó) ficavam ~3 px mais baixos: o pygame aumenta a imagem por cima quando o acento passa do topo da fonte. Agora os textos são alinhados pela linha de base, usando as métricas da fonte (`texto.desenhar_centralizado`), e há teste para isso.
  3. O menu tinha uma faixa vazia no lugar do HUD. Agora o xadrez cobre a janela inteira.
- **Decisões de design:** a cobra volta ao tamanho inicial a cada nível (como no Snake clássico); "Jogar de novo" recomeça do nível escolhido no início da campanha, e não do nível em que o jogador morreu.
- **Verificado localmente:** ruff sem apontamentos, 82 testes passando, jogo aberto de verdade (`python -m cobrinha` e `--nivel 3 --debug`) e capturas de todas as telas novas conferidas.
- Próximo passo: **Fase 3** (pixel art, fonte pixel, menus com mouse, sons). Ela vai exigir baixar uma fonte de licença livre e criar ou baixar sons; vou pedir autorização antes de qualquer download.

### 2026-10-02 09:41 — Fase 3 (pixel art, fonte, sons e menus com mouse)

**Feito:**
- **Sprites em pixel art (I3, I4):** `ferramentas/gerar_sprites.py` desenha pixel a pixel, com a paleta do jogo, os PNGs de 25 × 25: cabeça (olhos, narinas e língua), corpo reto (com escamas em "V"), curva, cauda e maçã (brilho, cabinho e folha). O jogo gera as 4 direções por rotação de 90° (16 superfícies preparadas uma vez).
- **Peças da cobra:** `ui/pecas.py` escolhe, em função pura e testável, a peça e a rotação de cada segmento (cabeça, reto horizontal/vertical, as 4 curvas, cauda). Também trata vizinhos do outro lado do campo, já preparando o modo sem bordas da Fase 4. A comida "flutua" 1 px.
- **Fonte pixel (I6): VT323** (SIL OFL), com a licença no pacote. Escala de tamanhos em `TamanhoFonte` (`config.py`), escolhida medindo a espessura dos traços.
- **Sons (I8):** `ferramentas/gerar_sons.py` sintetiza, só com a biblioteca padrão, 9 efeitos chiptune (comer, nível, bater, vitória, navegar/confirmar no menu, bipes da contagem, pausa) e uma música em loop de 13,7 s (Am–F–C–G, 140 bpm). A saída é determinística (conferi o hash após regerar). Novo `audio.py`: toca efeitos e música, pausa a música na pausa, **M silencia em qualquer tela** e, sem dispositivo de áudio, o jogo segue em silêncio.
- **HUD novo (I2):** rótulos e valores de PONTOS/RECORDE, NÍVEL com **barra de progresso** da meta e aviso "MUDO (M)".
- **Menus com mouse (I1):** passar o mouse seleciona; clique confirma; nos itens ajustáveis, clicar nas pontas muda o valor. Sons de navegação e confirmação.
- **Transições (I7):** fade de entrada (0,25 s) a cada troca de tela; a contagem também pode ser pulada com clique.
- **Tela de créditos** (nova, no menu): autores da V2 e da V1, fonte (atribuição pedida pela OFL) e origem de sprites e sons.
- **Menu principal** redesenhado: título em pixel art e uma cobra decorativa feita com os próprios sprites.
- **Empacotamento (D6):** os assets entram no pacote (`package-data`); conferi que o wheel leva os 17 arquivos. Ícone da janela = a maçã.
- **Testes:** de 82 para **122**. Novos: `test_pecas.py` (11), `test_recursos.py` (17: tamanhos e transparência dos sprites, formato dos WAVs e regressão das maiúsculas acentuadas), `test_audio.py` (3, incluindo o jogo sem saída de áudio), mouse e sons no menu, fade, tecla M, créditos e sons da contagem e de comer.

**Arquivos:** `ferramentas/gerar_sprites.py` (novo), `ferramentas/gerar_sons.py` (novo), `src/cobrinha/assets/` (novos: 2 da fonte, 5 sprites, 10 sons), `pyproject.toml`, `src/cobrinha/config.py`, `src/cobrinha/recursos.py`, `src/cobrinha/audio.py` (novo), `src/cobrinha/jogo.py`, `src/cobrinha/ui/texto.py`, `src/cobrinha/ui/pecas.py`, `src/cobrinha/ui/hud.py`, `src/cobrinha/ui/menu.py`, `src/cobrinha/estados/navegacao.py`, `src/cobrinha/estados/jogando.py`, `src/cobrinha/estados/contagem.py`, `src/cobrinha/estados/pausa.py`, `src/cobrinha/estados/nivel_concluido.py`, `src/cobrinha/estados/fim_de_partida.py`, `src/cobrinha/estados/menu_principal.py`, `src/cobrinha/estados/creditos.py` (novo), `tests/conftest.py`, `tests/test_pecas.py` (novo), `tests/test_recursos.py` (novo), `tests/test_audio.py` (novo), `tests/test_menu.py`, `tests/test_jogo.py`, `tests/test_estados.py`, `briefing_v2.md`, `README.md`, `LOG.md`.

**Motivo / observações:**
- **Troca de fonte: Press Start 2P → VT323.** A Press Start 2P (baixada primeiro) encaixa tudo em 8 × 8 px. Nas maiúsculas acentuadas, a letra encolhe e "NÍVEL"/"CRÉDITOS" aparecem como "NíVEL"/"CRéDITOS"; Ó, Ô e Õ são idênticos às minúsculas (verificado comparando os bitmaps). Comparei três alternativas OFL lado a lado: a Silkscreen tem o mesmo problema; a Pixelify Sans fica com traços irregulares abaixo de 32 px; a **VT323** tem as maiúsculas acentuadas corretas e traços consistentes. A Press Start 2P não foi commitada. O teste `test_fonte_tem_maiusculas_acentuadas_de_verdade` impede a volta do problema.
- **Ajustes feitos a partir das capturas de tela:** escamas removidas da curva (ficavam distorcidas no arco), cobra decorativa do menu afastada do item "SAIR" e título do nível no HUD afastado da barra de progresso.
- **Downloads** (autorizados pelo João): fontes do repositório oficial `google/fonts` (Press Start 2P, Pixelify Sans, Silkscreen e VT323, só para comparação; apenas a VT323 e a licença dela ficaram no projeto). Nenhum som foi baixado; todos foram gerados por código.
- **Verificado localmente:** ruff sem apontamentos, 122 testes, jogo aberto com áudio real e `python -X dev` (sem avisos), capturas de todas as telas conferidas. Não dá para ouvir os sons por aqui: vale o João testar o volume e o gosto da música.
- Próximo passo: **Fase 4** (obstáculos nos níveis 2 e 3, fruta dourada, recordes salvos em disco, modos Clássico/Sem bordas, opções e efeitos visuais).

### 2026-10-02 10:54 — Correção do áudio baixo e som de mordida da maçã

**Feito:**
- **Diagnóstico** (o João relatou que o áudio "não estava funcionando"): o jogo abria o mixer no WASAPI e tocava normalmente. A saída padrão do Windows são os alto-falantes Cirrus Logic, com volume geral em 52%, e a sessão do python.exe estava a 100% e sem mudo. Medindo o pico do sinal que chegava ao Windows com o pycaw (só para diagnóstico, fora do projeto), a música chegava com pico de **0,20** e os efeitos com ~0,27: baixo demais para alto-falantes de notebook.
- **Causa:** a normalização do `gerar_sons.py` só **reduzia** o volume (`min(1, 0,9/pico)`), nunca aumentava. Somada aos volumes conservadores (efeitos 0,6 e música 0,35), deixava tudo uns 10 dB abaixo do ideal.
- **Correção:** todos os sons agora são normalizados para pico de 0,89 (−1 dBFS), com intensidade relativa por som (os de menu são mais discretos). Volumes padrão: efeitos 0,9 e música 0,5. Medido de novo: música com pico de **0,41** e efeitos de **0,81 a 0,97**.
- **Som de mordida** (pedido do João): o "comer" virou um "nhac!" crocante, com dois estalos de ruído filtrado (filtro passa-baixa de um polo) seguidos de um blip subindo, em 0,16 s.

**Arquivos:** `ferramentas/gerar_sons.py`, `src/cobrinha/config.py`, os 10 WAVs de `src/cobrinha/assets/sons/` (regerados), `LOG.md`.

**Motivo / observações:** a medição anterior conferia só se o mixer estava ativo, não se o som era audível. Daqui em diante, mudanças de áudio são conferidas também pelo pico que chega ao Windows.

### 2026-10-02 11:08 — Fase 4 (conteúdo: níveis com pedras, fruta dourada, modos, recordes e opções)

**Feito:**
- **Níveis com identidade (J4):** cada nível tem nome e mapa de pedras desenhado em texto (32 × 22, `#` = pedra): 1 "Campo aberto", 2 "Pedras no caminho" e 3 "Labirinto". Novo sprite `parede.png` (pedra cinza com luz, sombra e rachaduras). As pedras são desenhadas no fundo uma vez por nível.
- **Aceleração (J9):** +0,15 passo/s a cada comida dentro do nível. Para compensar, a velocidade base dos níveis 2 e 3 passou de 11 e 14 para 10 e 12 passos/s, chegando ao fim de cada nível perto da velocidade antiga.
- **Fruta dourada (J5):** 10% de chance depois de comer; vale +5 pontos, faz crescer, não conta para a meta, some em 5 s de jogo e pisca no último 1,5 s. Novo sprite `comida_dourada.png` e novo som `bonus.wav` (mordida + arpejo brilhante).
- **Modos (J8):** Clássico (bordas matam) e Sem bordas (a cobra atravessa). Escolha no menu principal; o modo aparece no HUD.
- **Recordes salvos (J6):** `Progresso` virou ranking top 5 **por modo** (pontos, nível alcançado e data), com colocação e desempate a favor de quem chegou antes. Nova tela **RECORDES** (← → troca o modo). O fim de partida mostra "NOVO RECORDE!" ou "TOP 5: 3º LUGAR".
- **Persistência:** novo `persistencia.py` grava progresso e opções em `%APPDATA%\Cobrinha\dados.json` (ou `~/.local/share/cobrinha`). A gravação é atômica (arquivo temporário + troca); arquivo corrompido vira `.corrompido` e o jogo segue com os padrões; valores inválidos voltam ao padrão. Todo salvamento passa pela `navegacao.py`.
- **Opções (I9):** nova tela com volume dos efeitos e da música (passos de 10%, aplicados na hora), tela cheia e efeitos visuais. Salvas ao sair.
- **Efeitos visuais (I10) e acessibilidade (I11, parcial):** "+1"/"+5" sobem e somem ao comer; a cobra pisca ~0,9 s ao bater antes da tela de fim (as teclas são ignoradas nesse intervalo). A opção "efeitos visuais: NÃO" desliga as duas coisas.
- **Testes:** de 122 para **171**. Novos: `test_persistencia.py` (8), `test_estados_fase4.py` (11), `test_efeitos.py` (1); +16 em `test_partida.py` (pedras, modos, aceleração, fruta dourada e partidas aleatórias em todos os níveis e modos); +9 em `test_niveis.py` (**busca em largura confirma que nenhum mapa tem área fechada**, faixa de partida livre, ranking por modo); +4 em `test_recursos.py`. As funções auxiliares dos testes de telas foram para `tests/auxiliares.py`. **Os testes usam uma pasta de dados temporária** (`COBRINHA_DADOS`), nunca a real.

**Arquivos:** `src/cobrinha/config.py`, `src/cobrinha/dominio/grade.py`, `src/cobrinha/dominio/niveis.py`, `src/cobrinha/dominio/partida.py`, `src/cobrinha/dominio/progresso.py`, `src/cobrinha/opcoes.py` (novo), `src/cobrinha/persistencia.py` (novo), `src/cobrinha/audio.py`, `src/cobrinha/jogo.py`, `src/cobrinha/ui/efeitos.py` (novo), `src/cobrinha/ui/pecas.py`, `src/cobrinha/ui/hud.py`, `src/cobrinha/estados/navegacao.py`, `src/cobrinha/estados/jogando.py`, `src/cobrinha/estados/contagem.py`, `src/cobrinha/estados/pausa.py`, `src/cobrinha/estados/nivel_concluido.py`, `src/cobrinha/estados/fim_de_partida.py`, `src/cobrinha/estados/menu_principal.py`, `src/cobrinha/estados/recordes.py` (novo), `src/cobrinha/estados/opcoes.py` (novo), `ferramentas/gerar_sprites.py`, `ferramentas/gerar_sons.py`, `src/cobrinha/assets/imagens/parede.png` (novo), `src/cobrinha/assets/imagens/comida_dourada.png` (novo), `src/cobrinha/assets/sons/bonus.wav` (novo), `tests/conftest.py`, `tests/auxiliares.py` (novo), `tests/test_estados.py`, `tests/test_estados_fase4.py` (novo), `tests/test_partida.py`, `tests/test_niveis.py`, `tests/test_persistencia.py` (novo), `tests/test_efeitos.py` (novo), `tests/test_recursos.py`, `README.md`, `briefing_v2.md`, `LOG.md`.

**Motivo / observações:**
- **Problema achado nas capturas:** as setas "← →" saíam **em branco** nos rodapés de Recordes e Opções. A VT323 informa métricas para elas, mas o glifo é vazio, e por isso a checagem de métricas da Fase 3 não pegou. Trocadas por "SETAS". Novo teste `test_todo_caractere_exibido_tem_desenho_na_fonte`: lê o código das telas, extrai todos os textos exibidos (sem docstrings) e confere se cada caractere gera pixels. Confirmei à parte que ele acusaria as setas.
- **Outro ajuste visual:** véu da contagem mais escuro (as pedras do nível 2 apareciam atrás do nome do nível).
- **Tropeço no processo:** usei `git stash` para tentar provar o teste acima, mas o stash também guardou o próprio arquivo de teste, e a checagem não valeu. Conferi em seguida que o `stash pop` devolveu tudo (stash vazio, 23 arquivos com as mesmas alterações) e fiz a prova do jeito certo.
- **Remapeamento de teclas** (parte do I11) continua no backlog da V3, como definido na seção 8.4.
- **Verificado localmente:** ruff sem apontamentos, 171 testes, jogo aberto com `-X dev` (menu e `--nivel 3 --debug`) usando uma pasta de dados temporária (nada foi gravado na pasta real do João) e capturas de todas as telas novas conferidas.
- Próximo passo: **Fase 5** (entrega: executável Windows com PyInstaller, GIF de demonstração no README e release `v2.0.0`).

### 2026-10-02 11:32 — Novo sistema de música (uma faixa por momento do jogo)

**Feito** (pedido do João: música menos repetitiva):
- **4 músicas** geradas por código em `ferramentas/gerar_sons.py`, cada uma com tom, andamento e timbre próprios. O gerador ganhou um "compositor" (`Faixa` + `compor`) no lugar da função única:

  | Arquivo | Momento | Tom | Andamento | Duração do loop |
  |---------|---------|-----|-----------|-----------------|
  | `musica_menu.wav` | Menu, recordes, opções, créditos | lá menor (Am–F–C–G), calma | 140 bpm | 13,7 s |
  | `musica_fase1.wav` | Fase 1, Campo aberto | dó maior (C–G–Am–F), alegre | 150 bpm | 12,8 s |
  | `musica_fase2.wav` | Fase 2, Pedras no caminho | ré menor (Dm–B♭–F–C), sincopada | 160 bpm | 12,0 s |
  | `musica_fase3.wav` | Fase 3, Labirinto | mi menor (Em–C–D–B), rápida e tensa | 172 bpm | 11,2 s |

  A música do menu é **byte a byte idêntica** à antiga `musica.wav` (mesmo hash), que foi removida do repositório.
- **Regras da música de fundo** (`src/cobrinha/audio.py`):
  1. **Menu e telas ligadas a ele** tocam a música do menu (`Musica.MENU`).
  2. **Ao sair do menu e a partida começar de fato**, a música muda para a da fase (`EstadoJogando` chama `tocar_musica(musica_da_fase(n))`).
  3. **A cada troca de fase** a música alterna: fase 1 → 2 → 3. `musica_da_fase` reveza as faixas se um dia houver mais fases que músicas.
  4. **Ao bater (game over)** a música **para na hora**, no mesmo passo da batida e antes da animação e da tela de fim (`parar_musica()`). O jogo fica em silêncio até voltar ao menu, onde a música do menu volta.
  5. **Na pausa** a música pausa e continua de onde parou.
- **API nova do `Audio`:** enum `Musica`; `tocar_musica(musica)` troca de faixa e não reinicia se ela já for a atual; `parar_musica()`; atributo `musica_atual` (None = silêncio), que segue correto mesmo sem saída de áudio. Saiu a constante `ARQUIVO_MUSICA`.
- **Testes:** de 171 para **188**. Novo `tests/test_musica.py` (10, cobrindo a música em cada momento do jogo, inclusive "parou já na batida, antes da tela de fim"), `tests/test_audio.py` reescrito (6) e `tests/test_recursos.py` checando os 4 WAVs e que as músicas são diferentes entre si.

**Arquivos:** `ferramentas/gerar_sons.py`, `src/cobrinha/assets/sons/musica.wav` (removido), `src/cobrinha/assets/sons/musica_menu.wav`, `musica_fase1.wav`, `musica_fase2.wav`, `musica_fase3.wav` (novos), `src/cobrinha/audio.py`, `src/cobrinha/estados/menu_principal.py`, `src/cobrinha/estados/jogando.py`, `tests/test_audio.py`, `tests/test_musica.py` (novo), `tests/test_recursos.py`, `README.md`, `LOG.md`.

**Motivo / observações:**
- **Interpretações** (o pedido não cobria esses casos): "Jogar de novo" direto da tela de fim **é** um começo de partida, então toca a música da fase (o silêncio vale para a tela de fim). A **vitória** também para a música, para a fanfarra de vitória soar sozinha.
- **Nível medido no Windows** (pycaw, fora do projeto): as 4 músicas chegam com pico de 0,40 a 0,41 (nenhuma fase mais alta que outra) e, depois de `parar_musica()`, o pico vai a 0,00.
- O `musica.wav` antigo saiu do repositório com `git rm --cached`, porque o jogo do João estava aberto e o Windows travava o arquivo. A cópia local pode ser apagada depois de fechar o jogo; ela não é mais usada.

### 2026-10-02 11:39 — Fase 5 (entrega: executável, GIF, release e versão 2.0.0)

**Feito:**
- **Versão 2.0.0** no `pyproject.toml` e em `cobrinha.__version__`. Novo extra `[ferramentas]` (PyInstaller e Pillow), separado do `[dev]`.
- **Executável Windows:** `ferramentas/empacotar.py` gera o ícone `.ico` a partir do sprite da maçã (ampliado com NEAREST, em 6 tamanhos), inclui **só os assets versionados no Git** (`git ls-files`), roda o PyInstaller (arquivo único, sem console, entrada em `ferramentas/iniciar_jogo.py`) e termina com um **teste de fumaça**: abre o `.exe` no nível 3 com `--fechar-em 3` e exige saída sem erro. Resultado local: `dist/Cobrinha.exe` com 15,2 MB, teste ok e 23 assets dentro (conferido com o leitor de arquivos do PyInstaller).
- **`--fechar-em SEGUNDOS`:** agenda um evento QUIT, e o jogo encerra pelo caminho normal. Usado no teste do executável (local e no CI) e coberto por teste.
- **GIF de demonstração** (`docs/demo.gif`, 600 × 450, 15 fps, 14,3 s, 0,2 MB): `ferramentas/gravar_demo.py` joga o jogo de verdade, sem janela, com um piloto automático (busca em largura até a comida, desviando do corpo e das pedras). Roteiro: menu → contagem do nível 2 → partida com maçã dourada → batida → tela de fim. Semente fixa, então o GIF sai sempre igual.
- **`Cobra.tem_comandos_pendentes`:** propriedade pública usada pelo piloto, para não acessar o atributo privado da fila de direções.
- **Release automatizada:** `.github/workflows/release.yml` dispara com uma tag `v*`, roda os testes no Windows, gera e testa o executável a partir do repositório limpo e cria a release com o `.exe` anexado e as notas de `docs/notas-<tag>.md`.
- **README:** GIF no topo, selo da release, seção "Baixar e jogar (Windows)" (com o aviso do SmartScreen), comandos de empacotamento e de gravação do GIF, e como publicar uma versão.
- **Testes:** de 188 para **190** (`--fechar-em` com o loop real; `tem_comandos_pendentes`).

**Arquivos:** `pyproject.toml`, `src/cobrinha/__init__.py`, `src/cobrinha/__main__.py`, `src/cobrinha/dominio/cobra.py`, `ferramentas/empacotar.py` (novo), `ferramentas/iniciar_jogo.py` (novo), `ferramentas/gravar_demo.py` (novo), `docs/demo.gif` (novo), `docs/notas-v2.0.0.md` (novo), `.github/workflows/release.yml` (novo), `tests/test_cobra.py`, `tests/test_jogo.py`, `README.md`, `briefing_v2.md`, `LOG.md`.

**Motivo / observações:**
- **O executável publicado é gerado pelo CI, não pela máquina do João:** assim ele é reproduzível e não carrega nada solto da pasta local (ex.: o `musica.wav` antigo, que continua travado pelo jogo aberto).
- O teste de fumaça local abriu uma janela do jogo por ~3 s na tela do João; no CI ele roda com o driver de vídeo `dummy`.
- O executável não tem assinatura digital (certificado pago), então o Windows SmartScreen pode avisar na primeira execução. Isso está explicado no README e nas notas da release.
- A release `v2.0.0` é criada em seguida, pela tag; o resultado fica registrado na próxima entrada.

### 2026-10-02 11:43 — Release v2.0.0 publicada

**Feito:**
- Tag `v2.0.0` criada sobre o commit `4997e12`, depois do CI verde nos 4 ambientes.
- O workflow **Release** rodou no Windows do GitHub: dependências → 190 testes → executável gerado e testado → release publicada. Todas as etapas com sucesso.
- **Release:** <https://github.com/Joaofernandes-DEV/v2_jogoCobrinha/releases/tag/v2.0.0>, com o anexo `Cobrinha.exe` (15,3 MB) e as notas de `docs/notas-v2.0.0.md`. Não é rascunho nem pré-lançamento.
- **Conferência independente:** baixei o `Cobrinha.exe` publicado e rodei com `--fechar-em 2 --nivel 3` (driver de vídeo `dummy` e pasta de dados temporária): saída 0 e `dados.json` gravado.

**Arquivos:** `LOG.md`.

**Motivo / observações:**
- **Roteiro da V2 concluído:** Fases 0 a 5 ✅. O que ficou para depois está na coluna "Fica para a V3" da seção 8.4 do briefing (remapeamento de teclas, power-ups extras, ranking online, partículas, movimento interpolado, versão web etc.).
- **Para o João fazer:** apagar o arquivo local solto `src/cobrinha/assets/sons/musica.wav` depois de fechar o jogo (ele não está mais no repositório nem no executável), e testar o som do executável num PC sem Python.

### 2026-10-02 16:02 — Guia de contribuição e proteção da `main`

**Feito:**
- Criado o `CONTRIBUTING.md` com o fluxo para colaboradores: branch, testes (`ruff` e `pytest`), entrada no `LOG.md`, um commit por arquivo (Conventional Commits em português) e Pull Request.
- Criado o `CLAUDE.md` com o mesmo fluxo resumido, para que o Claude Code de quem colaborar siga o padrão automaticamente.
- Configurada a descrição e os topics do repositório no GitHub.
- Proteção da branch `main`: exige Pull Request e os 4 checks do CI (Linux 3.11, 3.12 e 3.13; Windows 3.11) verdes antes do merge. Branch desatualizada em relação à `main` é bloqueada e force-push e exclusão da `main` são proibidos. O dono (admin) pode ignorar a regra em emergências.

**Arquivos:** `CONTRIBUTING.md` (novo), `CLAUDE.md` (novo), `LOG.md`.

**Motivo / observações:**
- O colaborador vai implementar no mesmo padrão adotado até aqui; documentar o fluxo evita depender de explicação verbal.
- A proteção foi aplicada depois do push destes arquivos, pois ela bloqueia push direto na `main`.

### 2026-10-02 22:43 — João Pedro Sinhorini Silva nos créditos da V2

**Feito:**
- A tela de créditos passou a listar **João Pedro Sinhorini Silva** como colaborador na seção "V2".
- O README ganhou o mesmo crédito na seção "Créditos".
- Novo teste garante que o nome aparece na seção V2 e que a lista maior ainda cabe na janela (o rodapé "voltar" não sai da tela).

**Arquivos:** `src/cobrinha/estados/creditos.py`, `tests/test_estados.py`, `README.md`, `LOG.md`.

**Motivo / observações:**
- João Pedro entra como colaborador do projeto. Ele já constava nos créditos da V1; agora também consta na V2.
- Ele vai implementar uma versão do modo "Contra o tempo" e subir depois; essa entrega será registrada quando acontecer.

### 2026-10-02 22:44 — Início da V3: movimento interpolado (suave)

**Feito:**
- A cobra deixou de "pular" de célula em célula: cada segmento desliza da célula anterior até a atual ao longo do tempo de cada passo. A lógica continua em passo fixo e discreta; só o desenho é interpolado.
- `Cobra.trajetos`: para cada segmento, de onde veio no último passo e onde está (segmentos nascidos do crescimento ficam parados).
- `Partida.progresso_passo`: quanto do passo atual já passou (0 a 1); fica em 1 com a partida encerrada.
- `interpolar_celula` (`ui/campo.py`) calcula a posição entre duas células. No modo **Sem bordas** o segmento sai por um lado e entra pelo outro, em vez de cruzar o campo inteiro; a peça é desenhada nos dois lados da borda e nunca invade o HUD.
- `Sprites.desenhar_cobra` ganhou o parâmetro `progresso` (padrão 1, que mantém o desenho antigo, usado pela cobra do menu).
- Testes de 191 para **200**.

**Arquivos:** `src/cobrinha/dominio/cobra.py`, `src/cobrinha/dominio/partida.py`, `src/cobrinha/ui/campo.py`, `src/cobrinha/ui/pecas.py`, `src/cobrinha/estados/jogando.py`, `tests/test_cobra.py`, `tests/test_partida.py`, `tests/test_pecas.py`, `LOG.md`.

**Motivo / observações:**
- É o primeiro item do backlog da V3 ("Movimento interpolado/suave", seção 8.4 do briefing). O nome do jogo e o título da janela seguem os mesmos.
- As regras (colisão, comer, pontos) continuam acontecendo no passo discreto, então os testes do domínio e o comportamento do jogo não mudam. O efeito colateral é que o desenho fica até um passo atrás da lógica: a comida some quando a cabeça chega à célula na lógica, um instante antes de a cabeça terminar de deslizar até ela.
- Os sprites seguem presos à grade (a orientação de curvas e cabeça muda por célula); a suavização é só de posição.
- A versão do pacote continua `2.0.0`; o número da V3 será definido na publicação.
- Esta branch parte de `docs/creditos-joao-pedro`, que precisa entrar na `main` primeiro.

### 2026-10-02 22:55 — V3: fruta de câmera lenta e outros power-ups

**Feito:**
- Três power-ups novos, que às vezes aparecem depois de comer (chance de 8%, um por vez no campo) e somem em 7 s se não forem pegos. Pegar um não dá pontos nem faz crescer.
  - **Câmera lenta** (fruta azul com relógio): a cobra anda na metade da velocidade por 5 s. Com os efeitos visuais ligados, o campo fica azulado.
  - **Pontos em dobro** (cereja dupla): por 8 s, cada comida vale 2 e a maçã dourada vale 10. A meta do nível continua contando 1 por comida.
  - **Encolher** (cogumelo): tira 3 segmentos da cauda na hora, sem deixar a cobra menor que o tamanho inicial. Se ela ainda estava para crescer, esse crescimento é cancelado primeiro.
- Os efeitos contam tempo de jogo (param na pausa). Pegar de novo um efeito ativo renova a duração, sem somar, e todos acabam ao trocar de nível.
- O HUD mostra os efeitos ativos com os segundos restantes (ex.: `LENTO 4  X2 7`). Ao pegar, sobe um texto azul (`LENTO!`, `X2!`, `-3`) e toca um som próprio. Como a fruta dourada, o power-up pisca quando está para sumir.
- Novo módulo `dominio/power_ups.py`, com os tipos e as durações; `Cobra.encolher`; `Evento.PEGOU_POWER_UP`; constantes no `config.py`.
- Sprites `power_camera_lenta`, `power_pontos_em_dobro` e `power_encolher` gerados por `ferramentas/gerar_sprites.py`; som `power_up` gerado por `ferramentas/gerar_sons.py`. Os assets antigos foram regenerados e saíram idênticos.
- README: power-ups em "Como jogar" e o novo módulo na estrutura.
- Testes de 200 para **222** (novo `tests/test_power_ups.py`; sprites novos em `tests/test_recursos.py`).

**Arquivos:** `src/cobrinha/config.py`, `src/cobrinha/dominio/power_ups.py` (novo), `src/cobrinha/dominio/cobra.py`, `src/cobrinha/dominio/partida.py`, `src/cobrinha/audio.py`, `src/cobrinha/ui/pecas.py`, `src/cobrinha/ui/hud.py`, `src/cobrinha/estados/jogando.py`, `ferramentas/gerar_sprites.py`, `ferramentas/gerar_sons.py`, `src/cobrinha/assets/imagens/power_camera_lenta.png` (novo), `src/cobrinha/assets/imagens/power_pontos_em_dobro.png` (novo), `src/cobrinha/assets/imagens/power_encolher.png` (novo), `src/cobrinha/assets/sons/power_up.wav` (novo), `tests/test_power_ups.py` (novo), `tests/test_recursos.py`, `README.md`, `LOG.md`.

**Motivo / observações:**
- Item "Fruta de câmera lenta e outros power-ups" do backlog da V3 (seção 8.4 do briefing).
- O sorteio do power-up usa o mesmo gerador aleatório da partida. Por isso, com `--semente`, a sequência de comidas muda em relação à V2 (continua reproduzível). O GIF de demonstração não foi regravado.
- Apagado o arquivo local solto `src/cobrinha/assets/sons/musica.wav`, a pedido do João. Ele não estava no repositório, então não gera commit.
- Esta branch parte de `feat/v3-movimento-suave`.

### 2026-10-02 23:07 — Volta ao movimento célula a célula

**Feito:**
- Removido o movimento interpolado (suave) da entrada "Início da V3". A cobra voltou a andar célula a célula, como na V2.
- Saíram `Cobra.trajetos`, `Partida.progresso_passo`, `interpolar_celula` e o parâmetro `progresso` de `Sprites.desenhar_cobra`, junto com os testes deles.
- Os power-ups continuam iguais.
- Testes de 222 para **213**.

**Arquivos:** `src/cobrinha/dominio/cobra.py`, `src/cobrinha/dominio/partida.py`, `src/cobrinha/ui/campo.py`, `src/cobrinha/ui/pecas.py`, `src/cobrinha/estados/jogando.py`, `tests/test_cobra.py`, `tests/test_partida.py`, `tests/test_pecas.py`, `LOG.md`.

**Motivo / observações:**
- O João testou o movimento suave e preferiu o movimento discreto, fiel ao clássico e à pixel art (a decisão original do D1 no briefing).
- A remoção foi feita depois do merge dos PRs #1 a #3, para o histórico registrar a tentativa e a volta.

### 2026-10-03 09:52 — README e GIF de demonstração com as novidades da V3

**Feito:**
- **GIF de demonstração regravado:** o piloto automático agora também pega os power-ups. No `docs/demo.gif` aparecem a câmera lenta (campo azulado, `LENTO` no HUD) e a cereja de pontos em dobro (`X2` no HUD e `+2` ao comer), além da maçã dourada.
- `ferramentas/gravar_demo.py`: o piloto mira primeiro no power-up, e a escolha da célula perto da cabeça virou a função `celula_livre_perto`, usada pela maçã dourada e pelos power-ups.
- **README:** nova seção "Novidades da V3 (em desenvolvimento)" com uma tabela dos power-ups. Cada linha mostra o sprite direto de `src/cobrinha/assets/imagens/`. A seção avisa que a versão para download ainda é a `v2.0.0` e anuncia o modo Contra o tempo do João Pedro. Em "Como jogar", os power-ups agora apontam para essa seção, e a legenda do GIF foi atualizada.

**Arquivos:** `ferramentas/gravar_demo.py`, `docs/demo.gif`, `README.md`, `LOG.md`.

**Motivo / observações:**
- Os sprites (`power_*.png`) e o som (`power_up.wav`) dos power-ups já estavam em `src/cobrinha/assets/` desde o PR #3. Faltava mostrar as novidades no material visual do projeto.
- O GIF tem 226 quadros e 0,2 MB, então continua leve para o README.

### 2026-10-03 09:59 — Preparação da release v3.0.0

**Feito:**
- Versão do pacote: `2.0.0` → **`3.0.0`** em `pyproject.toml` e `src/cobrinha/__init__.py`.
- Criadas as notas da release, `docs/notas-v3.0.0.md`, no mesmo formato das da v2.0.0: como jogar, power-ups, o crédito do colaborador João Pedro e o modo Contra o tempo anunciado para uma próxima versão.
- README: a seção "Novidades da V3" deixou de dizer "em desenvolvimento" e aponta para o executável da última release. O exemplo de "Publicar uma versão" agora usa `v3.0.1`.

**Arquivos:** `pyproject.toml`, `src/cobrinha/__init__.py`, `docs/notas-v3.0.0.md` (novo), `README.md`, `LOG.md`.

**Motivo / observações:**
- O João pediu o executável novo em *Assets* e escolheu publicar como release **v3.0.0**. A v2.0.0 continua publicada como está.
- O nome do jogo e o título da janela continuam os mesmos ("Jogo da Cobrinha V2"), conforme combinado no início da V3.
- Depois do merge, a tag `v3.0.0` dispara o workflow **Release**, que roda os testes no Windows, gera e testa o `Cobrinha.exe` e cria a release com ele anexado. O resultado fica registrado na próxima entrada.

### 2026-10-03 10:24 — Release v3.0.0 publicada

**Feito:**
- Tag `v3.0.0` criada sobre o commit `ebf7e88` (merge do PR #6), depois de o CI ficar verde nos 4 ambientes.
- O workflow **Release** rodou no Windows do GitHub e todas as etapas passaram: dependências → testes → executável gerado e testado → release publicada.
- **Release:** <https://github.com/Joaofernandes-DEV/v2_jogoCobrinha/releases/tag/v3.0.0>, com o anexo `Cobrinha.exe` (16,1 MB, sha256 `573f699f…cebf36`) e as notas de `docs/notas-v3.0.0.md`. Ela não é rascunho nem pré-lançamento e virou a **Latest**. A v2.0.0 continua publicada.
- **Conferência independente:** baixei o `Cobrinha.exe` publicado e o sha256 bate com o da release. Rodei com `--fechar-em 2 --nivel 3` (driver de vídeo `dummy` e pasta de dados temporária): saiu com código 0 e gravou o `dados.json`. O executável contém os sprites `power_camera_lenta`, `power_pontos_em_dobro` e `power_encolher` e o som `power_up.wav`.

**Arquivos:** `LOG.md`.

**Motivo / observações:**
- O João pediu o executável novo em *Assets* da página de releases. A V3 sai com os power-ups, o crédito do colaborador João Pedro e o movimento célula a célula da V2.
- O teste automático não exercita o áudio nem a janela real. Vale o João abrir o executável num PC sem Python para conferir o som e os power-ups jogando.
- Próximo passo da V3: o modo Contra o tempo, do João Pedro.

### 2026-10-03 13:42 — Modo contra o tempo (João Pedro Sinhorini Silva)

**Feito:**
- **Terceiro modo de jogo, `Modo.CONTRA_O_TEMPO`** (item do backlog da V3), feito pelo colaborador João Pedro. Regras: relógio de **60 s**, **+3 s** por maçã, **+5 s** pela maçã dourada e teto de **99 s**. As bordas matam, como no Clássico. Não há meta de comidas: o nível escolhido define só o mapa e a velocidade. A partida acaba quando o tempo esgota, quando a cobra bate ou quando ela vence (campo cheio).
- **Domínio (`partida.py`):**
  - Novos `Situacao.TEMPO_ESGOTADO` e `Evento.TEMPO_ESGOTADO`.
  - `Partida.tempo_restante` (None nos outros modos) e `tem_meta`.
  - O relógio é descontado depois dos passos do quadro e nunca anda mais que o limite de passos recuperáveis. Assim, um travamento (ex.: arrastar a janela) não rouba segundos do jogador.
- **Interface:**
  - O HUD troca a barra de progresso pelo relógio (`TEMPO 42`), que fica vermelho a partir de 10 s.
  - O texto flutuante ao comer mostra também os segundos ganhos (`+1  +3s`).
  - A contagem inicial ganha uma linha com as regras.
  - A tela de fim mostra **TEMPO ESGOTADO!** e toca o som de nível quando o tempo acaba.
- **Menu e recordes com 3 modos:** `Opcoes.alternar_modo(delta)` circula nos dois sentidos, e a tela de recordes passou a respeitar `←` e `→`. O ranking do modo é separado (`CONTRA_O_TEMPO`), e os `dados.json` antigos continuam válidos.
- **Integração com a V3** (o patch original foi feito sobre a v2.0.0):
  - Conflitos resolvidos em `config.py`, `partida.py`, `jogando.py`, `hud.py`, `README.md` e `LOG.md`, mantendo os power-ups.
  - O texto flutuante considera os pontos em dobro (`+2  +3s`). O bônus de segundos não dobra.
  - Ao acabar o tempo, o power-up que estiver no campo também é retirado (o patch original só retirava a maçã e a dourada).
  - No HUD, o relógio fica no centro e os power-ups ativos à esquerda, sem sobreposição.
  - README: as regras foram para "Como jogar", e a seção "Novidades da V3" passou a apresentar o modo.
  - A entrada do patch original (datada de 2026-10-02 18:37) foi refeita aqui, no final do LOG, com a data da integração.
- **Testes:** de 213 para **240**. Novo `tests/test_contra_o_tempo.py`, que cobre regras do relógio, bônus, teto, fim por tempo, ausência de meta, power-ups no modo, HUD, menu, recordes e ranking. `test_alternar_modo_circula` foi atualizado para 3 modos.

**Arquivos:** `src/cobrinha/config.py`, `src/cobrinha/opcoes.py`, `src/cobrinha/dominio/partida.py`, `src/cobrinha/ui/hud.py`, `src/cobrinha/estados/jogando.py`, `src/cobrinha/estados/fim_de_partida.py`, `src/cobrinha/estados/contagem.py`, `src/cobrinha/estados/menu_principal.py`, `src/cobrinha/estados/recordes.py`, `src/cobrinha/estados/navegacao.py`, `tests/test_contra_o_tempo.py` (novo), `tests/test_persistencia.py`, `README.md`, `briefing_v2.md`, `LOG.md`.

**Motivo / observações:**
- Os valores do modo (60 s, +3 s, +5 s, teto de 99 s, alerta em 10 s) estão em `config.py` e podem ser ajustados sem mexer na lógica. Ainda falta testar jogando para calibrar o equilíbrio.
- A aceleração por comida do nível continua valendo. Como não há meta, quem come muito joga cada vez mais rápido.
- Não foi criado som novo: o fim por tempo reaproveita `nivel.wav`.
- A câmera lenta deixa a cobra mais lenta, mas o relógio continua no ritmo normal. Fica como sugestão fazer o relógio também desacelerar nesse modo.
- O patch chegou por arquivo, avaliado e corrigido pelo João Vitor com o Claude Code. O João Pedro sobe a versão corrigida pelo terminal dele.

### 2026-10-03 14:47 — Preparação da release v3.1.0

**Feito:**
- Versão do pacote: `3.0.0` → **`3.1.0`** em `pyproject.toml` e `src/cobrinha/__init__.py`.
- Criadas as notas da release, `docs/notas-v3.1.0.md`: como jogar e as regras do modo Contra o tempo, com o crédito ao João Pedro.
- README: a seção "Novidades da V3" passou a citar as duas versões, e o exemplo de "Publicar uma versão" agora usa `v3.1.1`.

**Arquivos:** `pyproject.toml`, `src/cobrinha/__init__.py`, `docs/notas-v3.1.0.md` (novo), `README.md`, `LOG.md`.

**Motivo / observações:**
- O João pediu o `Cobrinha.exe` atualizado em *Assets*, agora com o modo Contra o tempo (PR #8).
- O número escolhido foi **3.1.0**: o modo é uma funcionalidade nova e mantém compatível o que já existia, inclusive os `dados.json` salvos. A v3.0.0 continua publicada.
- Depois do merge, a tag `v3.1.0` dispara o workflow **Release**. O resultado fica registrado na próxima entrada.

### 2026-10-03 14:56 — Release v3.1.0 publicada

**Feito:**
- Tag `v3.1.0` criada sobre o commit `453082e` (merge do PR #9), depois de o CI ficar verde nos 4 ambientes.
- O workflow **Release** rodou no Windows do GitHub e todas as etapas passaram: dependências → testes → executável gerado e testado → release publicada.
- **Release:** <https://github.com/Joaofernandes-DEV/v2_jogoCobrinha/releases/tag/v3.1.0>, com o anexo `Cobrinha.exe` (16,1 MB, sha256 `79615216…76a492`) e as notas de `docs/notas-v3.1.0.md`. Ela não é rascunho nem pré-lançamento e virou a **Latest**. A v3.0.0 e a v2.0.0 continuam publicadas.
- **Conferência independente:** baixei o `Cobrinha.exe` publicado e o sha256 bate com o da release. Rodei com `--fechar-em 2 --nivel 1` (driver de vídeo `dummy` e pasta de dados temporária), partindo de um `dados.json` com o modo `CONTRA_O_TEMPO` escolhido: saiu com código 0 e manteve o modo ao salvar. Com o mesmo arquivo, o executável da v3.0.0 descarta o modo desconhecido e volta para `CLASSICO`. Isso confirma que o modo novo está no executável publicado.

**Arquivos:** `LOG.md`.

**Motivo / observações:**
- O João pediu o `Cobrinha.exe` atualizado em *Assets*. A v3.1.0 traz o modo Contra o tempo do colaborador João Pedro (PR #8), além dos power-ups da v3.0.0.
- O teste automático não exercita o áudio nem a janela real. Vale abrir o executável num PC sem Python e jogar uma partida no modo Contra o tempo.

### 2026-10-07 20:59 — Ebook didático de Computação Gráfica (PDF, ABNT)

**Feito:**
- Novo ebook em `docs/ebook/`: *Computação Gráfica na prática: o Jogo da Cobrinha em Python com pygame-ce*, em PDF (101 páginas, das quais cerca de 78 de texto), para colegas e professor da disciplina, no formato ABNT completo (NBR 14724:2024, 10520:2023 e 6023:2018). Sumário aprovado pelo João antes da escrita.
- 14 capítulos: introdução e história da CG; a evolução da V1 à V3; gráficos raster e buffer duplo; sistemas de coordenadas; laço de jogo e passo fixo; pipeline de desenho 2D; pixel art gerada por código; transformações geométricas; cor e quantização (median cut); transparência e composição alfa (Porter e Duff); animação, com o estudo de caso do movimento interpolado revertido; colisão, recorte e envolvimento de bordas; interface e som; considerações finais. Mais resumo, *abstract*, listas, glossário, exercícios (Apêndice A) e como gerar o ebook (Apêndice B).
- 25 referências, todas conferidas na web (editora, DOI ou documentação oficial) antes de citar; o que não deu para confirmar ficou de fora ou com data provável, como manda a NBR 6023.
- 29 figuras geradas por código: 5 fluxogramas pedidos (laço principal, passo fixo com acumulador, pilha de telas, passo da partida e pipeline do quadro), diagramas, gráficos, sprites ampliados pelo vizinho mais próximo e 9 capturas reais do jogo rodando sem janela (driver `dummy`).
- `gerar_ebook.py`: os trechos de código saem dos arquivos reais (ou de um commit, com `git show`) com os números de linha verdadeiros; seções, figuras, quadros e códigos são numerados sozinhos; o PDF é impresso pelo Edge/Chrome sem janela, e o sumário e as listas ganham as páginas lendo o *outline* do próprio PDF (segunda passada).
- Novo extra `[ebook]` no `pyproject.toml` (markdown e Pillow) e `tests/test_ebook.py` (4 testes, só biblioteca padrão): rótulos únicos, referências cruzadas válidas, toda figura gerada é citada e todo intervalo de código existe. Testes de 240 para **244**.
- README: o ebook entrou em "Documentos do projeto"; `docs/ebook/README.md` documenta o comando e a sintaxe dos textos.

**Arquivos:** `docs/ebook/` (novo: `README.md`, `figuras.py`, `capturas.py`, `gerar_ebook.py`, `estilo.css`, `metadados.toml`, `texto/*.md`, `figuras/*.png`, `ebook-computacao-grafica-cobrinha.pdf`), `tests/test_ebook.py` (novo), `pyproject.toml`, `README.md`, `LOG.md`.

**Motivo / observações:**
- Pedido do João: material didático que explique os conceitos de CG com embasamento em fontes confiáveis e mostre onde cada um aparece no código.
- **Achados ao escrever:** o `pygame.SCALED` usa vizinho mais próximo porque o pygame-ce 2.5.8 define a dica `SDL_HINT_RENDER_SCALE_QUALITY` como `nearest` (`src_c/display.c`), com escala inteira em janela e "pixels desiguais" em tela cheia. As capturas confirmam o operador *over*: a grama (142, 196, 78) sob o véu azul α 40 vira (130, 183, 94), e sob o véu da pausa logo depois, (57, 72, 48).
- **Tropeços na geração:** a VT323 não tem setas, `α` nem `⌊⌋`; o gerador de figuras troca esses símbolos e falha se sobrar algum sem desenho. O Edge, no Windows, devolve o controle antes de terminar o PDF, então o script espera o arquivo ficar completo. O *outline* do Chromium tira o espaço nas quebras de linha dos títulos, então a comparação é feita sem espaços.
- As figuras foram regeneradas e saíram idênticas (mesmo MD5). Nenhum sprite, som ou código do jogo mudou.
- **Para o João conferir:** o nome do(a) professor(a) fica vazio em `metadados.toml` (a linha some da folha de rosto) e a cidade da capa está como Osasco; ajuste se a sua unidade da UNIP for outra.

### 2026-10-07 21:32 — Ebook: autores, professora, cidade e sem o Apêndice B

**Feito** (pedido do João, revisando o PR do ebook):
- **Autores:** João Pedro Sinhorini Silva, que ajudou na produção da V2, entrou como coautor do ebook, ao lado de João Vitor Teixeira Fernandes, na capa e na folha de rosto. As fontes das figuras passaram de "elaborada pelo autor" para "elaborada pelos autores".
- **Folha de rosto:** "Professora: Stephany Oliveira".
- **Local:** Osasco → São Paulo.
- **Apêndice B removido** ("Como este ebook foi gerado"), e o texto deixou de dizer que o ebook, as figuras ou as capturas foram gerados por código. Saíram as menções a `docs/ebook/figuras.py` e `capturas.py` nas fontes das figuras e as frases na introdução, nos capítulos 5, 8, 12, 13 e 14, no Apêndice A, no resumo e no *abstract*. As normas da ABNT, antes citadas só no Apêndice B, agora são citadas na introdução.
- O PDF foi regenerado: 99 páginas.

**Arquivos:** `docs/ebook/metadados.toml`, `docs/ebook/gerar_ebook.py`, `docs/ebook/texto/*.md` (`apendice-b-como-gerar.md` removido), `docs/ebook/ebook-computacao-grafica-cobrinha.pdf`, `LOG.md`.

**Motivo / observações:**
- `metadados.toml` agora aceita uma lista de autores (`autores`) e o rótulo do professor (`rotulo_professor`).
- Os scripts e o `docs/ebook/README.md` continuam documentando como regenerar o PDF, para quem mantém o repositório; isso só não aparece mais no texto do ebook.
- Nos capítulos, "o autor" que se referia às decisões da V2 e da V3 virou "João Vitor", para não confundir com a autoria do ebook.

### 2026-10-08 13:45 — Roteiro e prompt do anúncio em motion design

**Feito:**
- Criado `docs/roteiro-motion.md` com o roteiro de 40 s do anúncio (11 cenas), a linha do tempo e o prompt completo para pedir o motion design em outra sessão do Claude.
- O prompt aponta para os assets da V2 (sprites, fonte, sons, paleta) e para as telas da V1 em `Py_JogoDaCobrinha/`, usadas só na cena 2.
- Os números do anúncio vieram do repositório (versão 3.1.0): 3 níveis, maçã dourada de 5 s, modo sem bordas, 3 power-ups, modo Contra o tempo e 240+ testes (244 na última execução).

**Arquivos:** `docs/roteiro-motion.md` (novo), `LOG.md`.

**Motivo / observações:**
- Pedido do João: um anúncio em motion design, sem narração, feito em outra sessão. O roteiro fica versionado para a sessão nova ler direto.
- O prompt manda não usar `creditos.png` da V1 nem nomes do grupo da V1, que fez o projeto em grupo.
- Nenhum código, sprite ou som mudou. `ruff check`, `ruff format --check` e `pytest` passaram (244 testes).

### 2026-10-08 16:48 — Controle de PS5 (DualSense), com vibração e luz

**Feito:**
- **Novo módulo `src/cobrinha/controle.py`:** o jogo passa a aceitar controle de videogame pelo SDL (DualSense do PS5, por USB ou Bluetooth, e outros que o Windows reconhece). Os botões viram "teclas virtuais", eventos `KEYDOWN` marcados com `controle=True`, num único ponto (`Jogo._processar_eventos`). Por isso todas as telas funcionam com o controle sem tratar nada de novo.
  - Direcional → setas; ✕ → Enter; ◯ → Esc; Options → `P`; Create → `M`.
  - O analógico esquerdo funciona como direcional, com zona morta (55% para valer e volta abaixo de 30% para valer de novo), para não repetir nem virar a cobra sem querer.
  - O controle pode ser conectado antes ou depois de abrir o jogo. Se ele desconectar no meio da partida, o jogo pausa (gera o mesmo evento de quando a janela perde o foco).
  - No menu principal, o ◯ não fecha o jogo; o Esc do teclado continua fechando.
- **Vibração** (`Vibracao` FRACA, MEDIA e FORTE): fraca ao comer, média na maçã dourada, nos power-ups e ao concluir o nível ou vencer, e forte ao bater ou quando o tempo do Contra o tempo acaba.
- **Luz do controle:** cada tela informa a cor em `Estado.cor_do_controle` (verde-claro por padrão). Na partida: verde jogando, azul na câmera lenta, amarela com pontos em dobro e vermelha ao bater ou com o relógio do Contra o tempo no alerta (≤ 10 s). A luz só é reenviada ao controle quando a cor muda.
- `Jogo._atualizar_quadro(dt)`: a atualização de cada quadro saiu do laço principal para um método próprio, que também acende a luz da tela do topo.
- README: seção "Controle de PS5 (DualSense)" com a tabela de botões, a vibração e a luz, e o novo módulo na estrutura.
- Testes de 244 para **270**. O novo `tests/test_controle.py` usa um controle falso e cobre os botões, o analógico com zona morta e sem repetição, a conexão e a desconexão, a vibração, a luz e a integração com menu, pausa, mudo e partida.

**Arquivos:** `src/cobrinha/controle.py` (novo), `src/cobrinha/jogo.py`, `src/cobrinha/estados/base.py`, `src/cobrinha/estados/menu_principal.py`, `src/cobrinha/estados/jogando.py`, `tests/test_controle.py` (novo), `README.md`, `LOG.md`.

**Motivo / observações:**
- Ideia do João para a V3: jogar com o controle do PS5. Não precisou de dependência nova: o pygame-ce 2.5.8 (SDL 2.32) já reconhece o DualSense e oferece vibração (`rumble`) e luz (`set_led`).
- **Teste real:** o João testou com o DualSense e funcionou tudo: direcional, analógico, botões, vibração e luz.
- **Executável:** gerado localmente com `ferramentas/empacotar.py`, passou no teste de fumaça (confirma que o módulo `pygame._sdl2.controller` entra no `.exe`).

### 2026-10-08 16:50 — Preparação da release v3.2.0

**Feito:**
- Versão do pacote: `3.1.0` → **`3.2.0`** em `pyproject.toml` e `src/cobrinha/__init__.py`.
- Criadas as notas da release, `docs/notas-v3.2.0.md`: como jogar, a tabela de botões do DualSense, a vibração e a luz.
- README: a seção "Novidades da V3" cita as versões de `v3.0.0` a `v3.2.0` e apresenta o controle de PS5, com link para a tabela de botões. O exemplo de "Publicar uma versão" agora usa `v3.2.1`.

**Arquivos:** `pyproject.toml`, `src/cobrinha/__init__.py`, `docs/notas-v3.2.0.md` (novo), `README.md`, `LOG.md`.

**Motivo / observações:**
- O João pediu o `.exe` novo com o suporte ao controle de PS5 (PR #13).
- O número escolhido foi **3.2.0**: o controle é uma funcionalidade nova e não muda nada do que já existia. A v3.1.0 continua publicada.
- Depois do merge, a tag `v3.2.0` dispara o workflow **Release**. O resultado fica registrado na próxima entrada.

### 2026-10-08 16:56 — Release v3.2.0 publicada

**Feito:**
- Tag `v3.2.0` criada sobre o commit `9eeca51` (merge do PR #14), depois de o CI ficar verde nos 4 ambientes.
- O workflow **Release** rodou no Windows do GitHub e todas as etapas passaram: dependências → testes → executável gerado e testado → release publicada.
- **Release:** <https://github.com/Joaofernandes-DEV/v2_jogoCobrinha/releases/tag/v3.2.0>, com o anexo `Cobrinha.exe` (16,1 MB, sha256 `c09c624f…b195759`) e as notas de `docs/notas-v3.2.0.md`. Ela não é rascunho nem pré-lançamento e virou a **Latest**. A v3.1.0, a v3.0.0 e a v2.0.0 continuam publicadas.
- **Conferência independente:**
  - baixei o `Cobrinha.exe` publicado e o sha256 bate com o da release;
  - rodei com `--fechar-em 2 --nivel 2` (driver de vídeo `dummy` e pasta de dados temporária): saiu com código 0 e gravou o `dados.json`;
  - o executável contém o módulo `cobrinha.controle` e o `pygame._sdl2.controller`, carregados ao abrir o jogo, já que os controles são iniciados junto com ele.

**Arquivos:** `LOG.md`.

**Motivo / observações:**
- O João pediu o `.exe` novo com o suporte ao controle de PS5 (PR #13). O controle já tinha sido testado por ele com o DualSense, rodando pelo código-fonte.
- O teste automático não usa um controle de verdade nem o áudio. Vale abrir o executável publicado com o DualSense conectado para conferir a vibração e a luz.

### 2026-10-08 17:38 — Modo Duelo, etapa 1: dois jogadores no teclado

**Feito:**
- **Domínio (`dominio/duelo.py`, novo):** `PartidaDuelo`, de 2 a 4 cobras no mesmo campo, todas andando no mesmo passo fixo. As colisões de um passo são julgadas juntas, como se todos tivessem andado:
  - borda, pedra ou corpo (o próprio ou o de outra cobra, incluindo a cabeça de antes do passo) eliminam; a cauda de quem não está crescendo conta como livre;
  - duas ou mais cabeças na mesma célula eliminam todas; cabeças que trocam de lugar também (cada uma entra no pescoço da outra);
  - a cobra eliminada some do campo; vence quem sobrar e, se todos forem eliminados no mesmo passo, é empate (`Evento.EMPATOU`, novo).
- **Itens e velocidade:** 2 maçãs no campo ao mesmo tempo (`COMIDAS_NO_DUELO`) e a maçã dourada. A velocidade é uma só e acelera com as maçãs de todos. Power-ups ficam para a etapa 3.
- **Nascimento como dados:** 4 posições em faixas horizontais diferentes; um teste confere, nos 3 mapas, que nenhuma cai em pedra e que há 6 células livres à frente sem cruzar o caminho das outras.
- **Cobras coloridas:** `PeleCobra` e `PELES` no `config.py` (verde, azul, amarela e vermelha, só com cores da paleta). O `gerar_sprites.py` gera as 4 peças em cada pele; 12 PNGs novos (`cabeca_azul.png` etc.). Os 10 sprites antigos saíram idênticos (mesmo hash).
- **Telas:** item **DUELO (2 JOGADORES)** no menu, abaixo de JOGAR; o "Nível inicial" escolhe o mapa e a velocidade. Contagem com a dica "J1: WASD   J2: SETAS". Nova `EstadoDuelo`: WASD move só o jogador 1 e as setas só o jogador 2; quem bate pisca e some. Nova `EstadoFimDoDuelo`: "JOGADOR 2 VENCEU!" na cor da cobra, ou "EMPATE!", com os pontos de cada um.
- **HUD do duelo:** pontos de cada jogador na cor da cobra (cinza e "FORA" quando eliminado), "DUELO" e o nome do mapa no meio. Já cabe 4 jogadores.
- **Pausa genérica:** nova `EstadoDePartida` (`estados/base.py`). A pausa pede à tela de baixo para reiniciar, abandonar ou guardar antes de sair; o `EstadoJogando` faz isso com o código de antes, então 1 jogador não muda. O duelo não entra nos recordes.
- **Menu mais compacto:** com 8 itens, o SAIR ficava em cima da cobra decorativa; o título subiu 10 px e o espaço entre os itens passou de 8 para 6 px.
- README: controles, regras do Duelo em "Como jogar", Novidades da V3 e estrutura.
- Testes de 270 para **368**: novos `tests/test_duelo.py` (colisões, cabeça com cabeça, troca de lugar, 3 cabeças, empate, vencedor, cauda que sai, maçãs, passo fixo, nascimentos e duelos aleatórios de 2 a 4 cobras nos 3 mapas) e `tests/test_estados_duelo.py` (menu, controles separados, pausa, eliminação, fim, sons e HUD); `tests/test_recursos.py` confere que **todo pixel de todo sprite é transparente ou da paleta**.

**Arquivos:** `src/cobrinha/config.py`, `src/cobrinha/dominio/partida.py`, `src/cobrinha/dominio/duelo.py` (novo), `ferramentas/gerar_sprites.py`, `src/cobrinha/assets/imagens/` (12 PNGs novos: `cabeca`, `corpo_reto`, `corpo_curva` e `cauda` em `_azul`, `_amarela` e `_vermelha`), `src/cobrinha/ui/pecas.py`, `src/cobrinha/ui/hud.py`, `src/cobrinha/estados/base.py`, `src/cobrinha/estados/pausa.py`, `src/cobrinha/estados/contagem.py`, `src/cobrinha/estados/jogando.py`, `src/cobrinha/estados/navegacao.py`, `src/cobrinha/estados/menu_principal.py`, `src/cobrinha/estados/duelo.py` (novo), `src/cobrinha/estados/fim_do_duelo.py` (novo), `tests/test_duelo.py` (novo), `tests/test_estados_duelo.py` (novo), `tests/test_recursos.py`, `tests/auxiliares.py`, `tests/test_estados.py`, `docs/ebook/texto/` (10 textos), `README.md`, `LOG.md`.

**Motivo / observações:**
- Primeira das 3 etapas do modo Duelo pedidas pelo João: 2 jogadores no teclado. A etapa 2 traz a tela "Quem joga?", até 4 jogadores com controles ligados pelo `instance_id`, luz e vibração individuais; a etapa 3, os power-ups disputados, o placar até 3 vitórias e a variante com relógio.
- `PartidaDuelo` é uma classe à parte, e não uma extensão da `Partida`, porque a `Partida` carrega meta, campanha, relógio e power-ups de 1 jogador. Ela reaproveita `Cobra`, `Grade`, `Nivel`, o sorteio de células e a `FrutaDourada`. A `Partida` só ganhou o `Evento.EMPATOU`, e os testes do domínio não mudaram.
- Decisões confirmadas pelo João: a cobra eliminada some; o DUELO fica abaixo de JOGAR. Para isso, dois testes de tela (`test_menu_so_oferece_niveis_liberados` e `test_creditos_abrem_pelo_menu_e_voltam`) passaram a achar o item pelo nome (`descer_ate`) em vez de contar as setas.
- O `Sprites._pecas` continua guardando as peças da cobra verde, porque um teste existente o usa; as outras peles ficam em `_pecas_da_pele`.
- **Ebook:** o `test_ebook.py` falhou porque o ebook cita o código por número de linha, e esta etapa muda arquivos citados. As 20 citações desses arquivos foram fixadas no commit em que o PDF foi gerado (`270f2fc`), e o PDF não mudou. Citações de outros arquivos que já estavam desatualizadas desde o PR do controle (ex.: `jogo.py`) ficaram como estavam, porque o ebook vai sair do repositório.
- Nesta etapa, o direcional do controle ainda vira "setas" e por isso move o jogador 2 (avisado no README). A vibração ainda vale para todos os controles e a luz não muda no duelo; as duas coisas ficam individuais na etapa 2.
- **Verificado localmente:** ruff sem apontamentos, 368 testes, capturas de todas as telas novas (menu, contagem, duelo no labirinto, eliminação, vitória, empate e HUD com 4 jogadores) e o jogo testado pelo João.

### 2026-10-08 18:06 — Modo Duelo, etapa 2: controles, luzes e tela "Quem joga?"

**Feito:**
- **Tela "Quem joga?"** (`estados/quem_joga.py`, nova), aberta pelo item **DUELO (2 A 4 JOGADORES)** do menu. São 4 vagas (verde, azul, amarela e vermelha), preenchidas na ordem de chegada:
  - WASD entra pelo lado esquerdo do teclado e as setas pelo direito (no máximo 2 no teclado);
  - cada controle entra com ✕; ✕ de quem já entrou começa, e ◯ tira o controle da vaga;
  - Enter começa com 2 a 4 jogadores, e Esc volta ao menu. A tela avisa "FALTA 1 JOGADOR".
- **Entradas** (`entradas.py`, novo): `Entrada` diz de onde vêm os comandos de cada jogador (teclado esquerdo, teclado direito ou um controle pelo `instance_id`). No duelo, o direcional de um controle move só a cobra dele e não vira mais as "setas" do teclado.
- **Controle** (`controle.py`):
  - as teclas virtuais levam o `controle_id`;
  - `vibrar(..., controle_id)` vibra um controle só;
  - `definir_luzes(padrao, por_controle)` dá uma cor a cada controle e só reenvia a cor quando ela muda;
  - o aviso de desconexão diz qual controle saiu (`controle_desconectado`).
- **Luzes:** cada tela pode dar cores próprias aos controles (`Estado.luzes_dos_controles`). O `Jogo` junta as cores de toda a pilha, então o duelo mantém as cores por baixo da pausa, da contagem e da tela de fim. No duelo:
  - o controle de cada jogador fica na cor da cobra dele, e cinza depois de eliminado;
  - os controles que não jogam ficam brancos.
- **Vibração individual:** só vibra o controle de quem comeu (fraca), pegou a maçã dourada (média), foi eliminado (forte) ou venceu (média).
- **Controle desconectado** (`estados/controle_desconectado.py`, nova): se sair o controle de um jogador vivo, o duelo para e mostra "JOGADOR 2: reconecte o controle e aperte X". O primeiro controle livre que apertar ✕ passa a ser dele, e o duelo volta com a contagem 3-2-1. Esc ou P abrem a pausa, para quem quiser desistir. Se o controle sair durante a pausa, o aviso aparece quando o duelo volta.
- "Jogar de novo" e "Reiniciar" mantêm os mesmos jogadores; a contagem mostra quem joga com o quê (ex.: "J1: WASD   J2: CONTROLE   J3: SETAS").
- README: tela "Quem joga?", luz e vibração no duelo, reconexão e `entradas.py` na estrutura.
- Testes de 368 para **405**: novos `tests/test_entradas.py`, `tests/test_quem_joga.py` e `tests/test_duelo_controles.py` (controles e teclado no mesmo duelo, duelo de 4, vibração e luz por jogador, desconexão e religação); acréscimos em `tests/test_controle.py` (id nas teclas, vibração e luz por controle, cores de toda a pilha). `tests/auxiliares.py` ganhou um controle falso com vários `instance_id`.

**Arquivos:** `src/cobrinha/controle.py`, `src/cobrinha/entradas.py` (novo), `src/cobrinha/estados/base.py`, `src/cobrinha/jogo.py`, `src/cobrinha/estados/duelo.py`, `src/cobrinha/estados/controle_desconectado.py` (novo), `src/cobrinha/estados/quem_joga.py` (novo), `src/cobrinha/estados/fim_do_duelo.py`, `src/cobrinha/estados/navegacao.py`, `src/cobrinha/estados/menu_principal.py`, `tests/auxiliares.py`, `tests/test_controle.py`, `tests/test_entradas.py` (novo), `tests/test_quem_joga.py` (novo), `tests/test_duelo_controles.py` (novo), `tests/test_estados_duelo.py`, `README.md`, `LOG.md`.

**Motivo / observações:**
- Segunda das 3 etapas do modo Duelo pedidas pelo João. Ele deixou as decisões de design desta etapa comigo.
- **Religação em vez de esperar o mesmo controle:** o SDL dá um `instance_id` novo ao controle que reconecta, então o vínculo antigo não sobrevive. Por isso o jogador sem controle fica com o primeiro controle livre que apertar ✕.
- **Branco para quem não joga:** a cor do J1 (verde-claro) era igual à cor geral dos controles, e não daria para ver qual controle está no duelo.
- Desconectar o controle de quem não está jogando, ou de quem já foi eliminado, não para o duelo. Nos modos de 1 jogador, qualquer desconexão continua pausando, como antes.
- Os testes de tela da etapa 1 que entravam no duelo direto pelo menu agora passam pela tela "Quem joga?".
- Para conferir que os testes novos pegam erros, quebrei de propósito duas regras (vibração indo para todos e o direcional do controle movendo quem joga nas setas): 5 testes falharam. Depois desfiz a quebra.
- **Verificado localmente:** ruff sem apontamentos, 405 testes, capturas das telas novas (menu, "Quem joga?" com 1 e 4 jogadores, contagem com 4 e aviso de controle desconectado) e o jogo aberto para o João testar antes dos commits.
- Próximo passo: **etapa 3** (power-ups disputados, placar até 3 vitórias e a variante com relógio).

### 2026-10-08 23:21 — Modo Duelo, etapa 3: power-ups disputados, rodadas e relógio

**Feito:**
- **Rodadas até 3 vitórias:**
  - novo `Placar` no domínio (`vitorias`, `rodada`, `registrar`, `nova_rodada` e `campeao`), com `VITORIAS_PARA_VENCER = 3` no `config.py`; empate não dá vitória a ninguém;
  - a tela de fim virou a tela de placar: "JOGADOR 2 VENCEU A RODADA!" ou "EMPATE!", os pontos e os quadradinhos das vitórias de cada um, e PRÓXIMA RODADA;
  - com 3 vitórias, a tela anuncia "JOGADOR n É O CAMPEÃO!", e JOGAR DE NOVO começa outra disputa com os mesmos jogadores;
  - o HUD mostra "RODADA n" e os quadradinhos ao lado de cada nome. A contagem mostra a rodada, o mapa e o modo;
  - "Reiniciar", na pausa, recomeça a disputa com o placar zerado.
- **O duelo segue o MODO do menu:**
  - **Clássico:** a borda elimina;
  - **Sem bordas:** a cobra atravessa a borda;
  - **Contra o tempo:** é a variante com relógio.
- **Variante com relógio:** 60 s por rodada (`TEMPO_DUELO_COM_RELOGIO`, sem bônus por maçã), no centro do HUD e vermelho a partir de 10 s.
  - Vence quem tiver mais pontos quando o tempo acabar; pontos iguais são empate.
  - Quem é eliminado sai do campo, mas os pontos dele continuam valendo.
  - A rodada acaba antes se não sobrar ninguém, ou se o último vivo já estiver na frente; se ele estiver atrás, continua até passar à frente, bater ou o tempo acabar.
- **Power-ups disputados**, sorteados como nos outros modos (8% depois de cada maçã, um por vez, somem em 7 s):
  - **câmera lenta:** os adversários vivos andam na metade da velocidade por 5 s, e quem pegou fica livre da lentidão (quem estava lento e pega inverte o efeito);
  - **cogumelo:** corta 3 segmentos da cauda dos adversários, sem deixá-los menores que 3;
  - **pontos em dobro:** por 8 s, só para quem pegou, e só aparecem com relógio, porque sem relógio os pontos não decidem a rodada.
- **Cobra lenta:** ela anda um passo sim, um passo não. No passo em que fica parada, o corpo inteiro dela, inclusive a cauda, é obstáculo. As curvas apertadas ficam guardadas até ela andar.
- **Interface dos power-ups:** som de power-up; o controle de quem pegou vibra médio e o dos atingidos vibra fraco; sobe o texto do efeito ("LENTO!", "-3", "X2!") na cor de quem pegou; o HUD mostra "LENTO 4" ou "X2 7" embaixo de cada nome. O texto de pontos mostra o valor dobrado ("+2").
- **Quem joga?** mostra o mapa, o modo e a regra ("Campo aberto   Contra o tempo   campeão: 3 vitórias").
- README: rodadas, modos e power-ups do duelo em "Como jogar", e a novidade atualizada.
- Testes de 405 para **445**: novos `tests/test_duelo_disputa.py` (power-ups, cobra lenta e colisões com ela parada, sem bordas, relógio, fim antecipado, placar e duelos aleatórios com muitos itens em todos os modos) e `tests/test_duelo_rodadas.py` (placar entre as rodadas, campeão, jogar de novo, reiniciar, modos do menu, relógio e power-ups na tela).

**Arquivos:** `src/cobrinha/config.py`, `src/cobrinha/dominio/duelo.py`, `src/cobrinha/ui/hud.py`, `src/cobrinha/estados/duelo.py`, `src/cobrinha/estados/fim_do_duelo.py`, `src/cobrinha/estados/navegacao.py`, `src/cobrinha/estados/quem_joga.py`, `tests/test_duelo_disputa.py` (novo), `tests/test_duelo_rodadas.py` (novo), `tests/test_estados_duelo.py`, `README.md`, `LOG.md`.

**Motivo / observações:**
- Terceira e última etapa do modo Duelo pedida pelo João. O equilíbrio dos power-ups e o duelo seguindo o MODO do menu foram confirmados por ele antes da implementação.
- Relógio sem bônus por maçã: no Contra o tempo de 1 jogador, comer devolve segundos; numa disputa, isso arrastaria a rodada.
- A VT323 não tem os símbolos ■ e □, então os quadradinhos das vitórias são desenhados como retângulos (`desenhar_vitorias`, no `hud.py`).
- O título da contagem passou de "DUELO" para "RODADA n", e o teste da etapa 1 que conferia o título foi ajustado.
- Para conferir que os testes novos pegam erros, quebrei de propósito duas regras (a cobra lenta andando sempre e o placar sem registrar vitórias): 9 testes falharam. Depois desfiz a quebra.
- **Verificado localmente:** ruff sem apontamentos, 445 testes, capturas das telas novas ("Quem joga?" com o modo, contagem, HUD com relógio, vitórias e efeitos, placar da rodada e campeão) e o jogo aberto para o João testar antes dos commits.
- Com esta etapa, o modo Duelo pedido está completo. Ele ainda não foi publicado em release.
