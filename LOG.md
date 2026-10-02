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
