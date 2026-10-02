# Briefing V2 — Jogo da Cobrinha

> Documento de planejamento da V2. Base: análise da V1 em `Py_JogoDaCobrinha/` (commit `d414f3d`).
> Toda alteração feita a partir deste plano deve ser registrada no [LOG.md](LOG.md).
>
> **Status:** decisões fechadas em 2026-10-02 (ver [seção 8](#8-decisões-tomadas)). Repositório: <https://github.com/Joaofernandes-DEV/v2_jogoCobrinha>.

---

## 1. Visão geral

A V1 é um Snake funcional em Pygame, feito para a disciplina de Computação Gráfica: 3 níveis de velocidade, telas de transição desenhadas no Canva, sprites direcionais para a cobra e um comando escondido para pular para o nível 3. Todo o jogo está em um único arquivo (`src/main.py`, 348 linhas).

O jogo cumpre o objetivo acadêmico, mas tem bugs que encerram o programa com erro, uma grade desalinhada, controles que matam o jogador injustamente e uma estrutura difícil de evoluir.

**Objetivo da V2:** transformar o protótipo em um jogo **estável, bem estruturado e agradável de jogar**, que sirva como peça de portfólio: código organizado em módulos, lógica testável, interface feita no código (não em imagens fixas), jogabilidade mais rica e uma identidade visual nova e coesa em pixel art.

---

## 2. Diagnóstico da V1

### 2.1 Bugs confirmados

Referências de linha em `Py_JogoDaCobrinha/Jogo da cobrinha/src/main.py`.

| ID | Problema | Onde | Efeito para o jogador |
|----|----------|------|-----------------------|
| **B1** | `pygame.quit()` é chamado e depois o código **continua desenhando** (créditos → "2", fechar a janela nos créditos, na tela de nível ou durante o jogo). | L68, L91, L97, L126, L143, L165, L247, L308 | O jogo fecha com `pygame.error: video system not initialized` em vez de sair limpo. |
| **B2** | **Grade desalinhada.** A cobra nasce em `x = 400`, que não é múltiplo de 30 (`400 % 30 = 10`); a comida nasce em múltiplos de 30. Além disso, 800 / 30 = 26,67, então sobra uma faixa de 20 px. | L175–L177, L219 | A cobra fica 10 px deslocada da comida; ela "come" por sobreposição parcial. Visual torto e colisão com a borda direita inconsistente. |
| **B3** | **Meia-volta suicida.** A direção é validada contra `cobra.direcao`, que muda a cada tecla. Andando para a direita, apertar ↑ e ← rápido (no mesmo tick) faz a cobra virar para a esquerda, dentro do próprio pescoço. | L250–L258 | Morte injusta, principalmente no nível 3 (16 ticks/s). |
| **B4** | O comando escondido diz "`n` + `3`" no comentário, mas o código verifica `K_4`. | L77–L82 | Comportamento diferente do documentado. |
| **B5** | Ao zerar o nível 3 e escolher "sair" na tela final, `jogo_principal` devolve `None`, que `main` interpreta como "voltar ao menu", após o `pygame.quit()`. | L307–L309, L332 | Mesmo erro de B1. |
| **B6** | Assets carregados por caminho relativo (`"assets"`), que depende da pasta de onde o jogo é executado. O README manda rodar `python src/main.py` na raiz, mas os assets estão em `Jogo da cobrinha/assets`. | L17; README | Seguindo o README, o jogo não abre. |
| **B7** | Se a cobra ocupar o tabuleiro inteiro, `Comida.reposicionar` entra em laço infinito. | L216–L230 | Travamento (raro, mas possível; não existe condição de vitória). |

### 2.2 Limitações de estrutura

- **Arquivo único** misturando configuração, carregamento de assets, telas, entidades e loop principal.
- **Estado global**: `tela` e as imagens são carregadas na importação do módulo; as classes desenham direto na variável global.
- **Fluxo de telas por laços aninhados**: cada tela tem seu próprio `while True`, e a navegação depende de valores de retorno mistos (`True`, `False`, `'nivel3'`, `None`, `'sair'`, `'menu'`). É daí que vêm B1 e B5.
- **Lógica acoplada ao Pygame**: movimento, colisão e regras de nível não podem ser testados sem abrir uma janela.
- **Nomes misturados** em português e inglês (`current_level`, `foods_eaten_in_level` ao lado de `pontuacao`, `cobra`).
- **Sem `requirements.txt`, `.gitignore` nem testes**; o README descreve uma estrutura de pastas que não é a real.

### 2.3 Limitações de interface

- Menus, créditos, game over e transição de fase são **imagens com o texto embutido**: mudar uma opção ou uma tecla exige refazer a arte.
- Navegação só por teclas numéricas e letras soltas (`1/2/3`, `Y/N/E`), sem mouse nem setas + Enter.
- Os sprites da cobra (até 840×462 px) são esticados para 30×30, então **ficam distorcidos**. O corpo não tem peças de curva, e `corpo_left` e `corpo_up` nunca são usados.
- `comida.jpg` não tem transparência (JPG), então aparece um quadrado de fundo.
- O fundo `Grama1.png` (319×161) é ampliado para 800×600 e fica borrado.
- HUD de texto solto sobre o campo, sem faixa própria; a pontuação pode cobrir a cobra.
- Sem som, sem pausa, sem recorde.

### 2.4 Limitações de jogabilidade

- A tela de "mudar de fase?" (Y/N) **interrompe o jogo no meio da partida** e mistura escolha de dificuldade com progressão.
- A tela de nível bloqueia por 3 s fixos e descarta qualquer tecla.
- A progressão é só velocidade: os 3 níveis jogam igual.
- Começa a andar imediatamente após a tela de nível, sem contagem.
- Não há condição de vitória por tabuleiro cheio (ver B7).

### 2.5 Limitações de desempenho

- `pygame.font.SysFont(...)` é criado **a cada chamada** de `mostrar_texto`, ou seja, 2× por quadro no jogo.
- Telas de menu rodam `while True` **sem `clock.tick`**: consomem 100% de um núcleo da CPU enquanto o jogador lê o menu.
- A taxa de desenho é a mesma da lógica (8–16 FPS), então a animação fica "aos trancos" e a entrada só é lida a cada tick.
- `list.insert(0, ...)` + colisões criando um `pygame.Rect` por segmento a cada tick: O(n) com alocação, desnecessário numa grade.
- Assets pesados para o uso: os sprites da cobra têm 75–222 KB cada, para virar 30×30 px; as telas têm até 760 KB.

> Na escala atual (cobra com dezenas de segmentos) nenhum desses pontos derruba o FPS. Mesmo assim vale corrigir: são más práticas que pesam no portfólio, e a CPU a 100% nos menus é perceptível em notebook.

---

## 3. Estrutura do código

### 3.1 Arquitetura proposta

Separar **domínio** (regras puras, sem Pygame), **estados/telas** (máquina de estados) e **infraestrutura** (assets, áudio, persistência).

```plaintext
V2/
├── pyproject.toml            # dependências, versão do Python, ponto de entrada
├── README.md
├── LICENSE
├── src/cobrinha/
│   ├── assets/               # dentro do pacote: achado via pathlib e empacotável pelo PyInstaller
│   │   ├── imagens/          # sprites pixel art 25 × 25
│   │   ├── sons/
│   │   └── fontes/           # fonte pixel TTF embarcada (não depender de SysFont)
│   ├── __main__.py           # `python -m cobrinha`
│   ├── config.py             # constantes: grade, cores, velocidades, teclas
│   ├── jogo.py               # classe Jogo: loop principal + gerenciador de estados
│   ├── dominio/              # SEM import de pygame → 100% testável
│   │   ├── grade.py          # Posicao (NamedTuple), Direcao (Enum), dimensões
│   │   ├── cobra.py          # movimento, crescimento, buffer de direção
│   │   ├── comida.py         # sorteio entre células livres
│   │   ├── niveis.py         # definição dos níveis (velocidade, meta, obstáculos)
│   │   └── partida.py        # regras: colisão, pontuação, progressão, vitória
│   ├── estados/
│   │   ├── base.py           # Estado: tratar_evento / atualizar / desenhar
│   │   ├── menu.py
│   │   ├── jogando.py
│   │   ├── pausa.py
│   │   ├── transicao_nivel.py
│   │   ├── game_over.py
│   │   ├── vitoria.py
│   │   ├── recordes.py
│   │   ├── opcoes.py
│   │   └── creditos.py
│   ├── ui/                   # botões, menus navegáveis, HUD, texto com cache
│   ├── recursos.py           # carregamento único de assets via pathlib
│   ├── audio.py              # efeitos e música, com controle de volume/mudo
│   └── persistencia.py       # recordes e opções em JSON
└── tests/
    ├── test_cobra.py
    ├── test_comida.py
    └── test_partida.py
```

### 3.2 Decisões técnicas

| # | Melhoria | Resolve |
|---|----------|---------|
| **E1** | **Máquina de estados**: um único loop em `Jogo`; cada tela é um `Estado` com `tratar_evento`, `atualizar(dt)` e `desenhar(superficie)`. Trocas de tela por `jogo.trocar_estado(...)` / `empilhar(...)` (a pausa é empilhada sobre o jogo). `pygame.quit()` existe em **um único lugar**. | B1, B5, laços aninhados |
| **E2** | **Grade lógica em células**, não em pixels. A cobra e a comida guardam `(coluna, linha)`; a conversão para pixels acontece só no desenho. Colisão vira comparação de tuplas/conjunto. | B2 |
| **E3** | **Caminhos com `pathlib`** relativos ao arquivo do pacote (`Path(__file__).resolve().parent`), independente da pasta de execução. Renomear arquivos com espaço (`game over.png` → `game_over.png`). | B6 |
| **E4** | **Domínio sem Pygame** (`dominio/`), com `Enum` para direções e `dataclass` para posições. Permite testes com `pytest` sem janela. | testabilidade |
| **E5** | **Configuração centralizada** em `config.py` (ou `dataclass` de configuração): tamanho da grade, velocidades por nível, meta de comidas, mapeamento de teclas. | números mágicos espalhados |
| **E6** | **Padronizar nomes em português** (identificadores, comentários e docstrings), seguindo a maior parte da V1; type hints em todas as funções públicas. | consistência |
| **E7** | **Ferramentas de qualidade**: `pyproject.toml`, `ruff` (lint + formatação), `pytest`, `.gitignore` para Python, GitHub Actions rodando lint e testes a cada push. | ausência de padrão |
| **E8** | **Comando escondido vira modo de depuração explícito** (ex.: argumento `--nivel 3` ou tecla só ativa com `DEBUG=True`). | B4 |

---

## 4. Interface (visual, áudio e usabilidade)

| # | Melhoria | Detalhe |
|---|----------|---------|
| **I1** | **Menus desenhados por código** | Título e fundo podem continuar sendo arte; opções viram botões renderizados, navegáveis por **setas + Enter** e **mouse**, com item selecionado destacado. Textos e teclas mudam sem refazer imagens. |
| **I2** | **HUD em faixa própria** | Faixa no topo (ex.: 50–60 px) fora da área jogável: pontuação, recorde, nível e **barra de progresso** até a próxima fase. |
| **I3** | **Sprites em pixel art para a grade** | Sprites 25 × 25 nativos, fundo transparente, com **peças de curva** para o corpo. As 4 direções são geradas por rotação (`pygame.transform.rotate`) a partir de uma peça base, em vez de 4 arquivos. Ver 8.3. |
| **I4** | **Comida em PNG com transparência** | Substituir `comida.jpg`. Opcional: leve animação de pulsar. |
| **I5** | **Fundo nítido** | Padrão xadrez de grama desenhado por código (duas cores da paleta alternadas por célula). Ajuda o jogador a enxergar a grade. |
| **I6** | **Fonte embarcada** | Fonte pixel `.ttf` de licença livre em `assets/fontes/`, garantindo a mesma aparência em qualquer máquina. |
| **I7** | **Transições suaves** | Fade entre telas; tela de nível com contagem **3‑2‑1** que pode ser pulada com Enter. |
| **I8** | **Som** | Efeitos (comer, subir de nível, morrer, navegar no menu) e música de fundo opcional; tecla **M** para mudo e volume nas opções. Usar sons de licença livre e creditá-los. |
| **I9** | **Tela de opções** | Volumes, modo de tela (janela/tela cheia) e modo de jogo (Clássico/Sem bordas), salvos em JSON. Setas e WASD funcionam sempre; remapeamento fica para a V3. |
| **I10** | **Feedback visual** | "+1"/"+5" subindo ao comer e cobra piscando ao morrer, antes do game over. Tremor de tela e partículas ficam para a V3. |
| **I11** | **Acessibilidade** | Contraste suficiente no HUD, não depender só de cor para informação, dois esquemas de teclas (setas/WASD) e opção para desligar o piscar. |

---

## 5. Jogabilidade

| # | Melhoria | Detalhe |
|---|----------|---------|
| **J1** | **Buffer de direção** | Fila de até 2 comandos; cada comando é validado contra a **última direção enfileirada**, e um é consumido por tick. Elimina a meia-volta suicida (B3) e torna as curvas rápidas responsivas. |
| **J2** | **Pausa** | `P` ou `Esc` pausa, com menu: continuar, reiniciar, voltar ao menu. Pausar automaticamente quando a janela perde o foco. |
| **J3** | **Progressão sem interrupção** | Ao bater a meta do nível, terminar a fase com uma tela de "Nível concluído" entre fases, e não no meio da partida. A escolha de dificuldade vai para o menu ("Começar no nível…", desbloqueado ao alcançar). |
| **J4** | **Níveis com identidade** | Além da velocidade: **obstáculos** (paredes internas) no nível 2, **layout de labirinto** no nível 3. Níveis definidos como dados (`niveis.py` ou JSON), fáceis de adicionar. |
| **J5** | **Comidas especiais** | Ex.: fruta dourada que vale +5 e some após alguns segundos; fruta que reduz temporariamente a velocidade. Probabilidade e efeitos configuráveis. |
| **J6** | **Recordes** | Top 5 salvo em JSON (pontuação, nível, data), com tela própria e aviso de "novo recorde!" no game over. |
| **J7** | **Condição de vitória** | Tabuleiro cheio ou nível final concluído: tela de vitória (usa a arte `fim_de_jogo.png`). Corrige B7. |
| **J8** | **Modos de jogo** | Clássico (paredes matam) e Sem bordas (atravessa as laterais). Opcional: modo contra o tempo. |
| **J9** | **Curva de dificuldade suave** | Pequeno aumento de velocidade dentro do nível a cada comida, além do salto entre níveis. Valores ajustados jogando, registrados no LOG. |
| **J10** | **Contagem antes de começar** | 3‑2‑1 ao iniciar e ao voltar da pausa, para o jogador não perder por reflexo. |

---

## 6. Desempenho

| # | Melhoria | Detalhe |
|---|----------|---------|
| **D1** | **Separar lógica de renderização** | Lógica em passo fixo (acumulador de tempo, `ticks_por_segundo` do nível) e desenho a 60 FPS com `clock.tick(60)`. A entrada é lida todo quadro, então o controle fica mais responsivo. O movimento continua discreto, célula a célula (interpolação fica para a V3). |
| **D2** | **`clock.tick` em todas as telas** | Com a máquina de estados (E1) isso vem de graça: um único loop com limite de FPS. Elimina os 100% de CPU nos menus. |
| **D3** | **Cache de fontes e textos** | Criar as fontes uma vez em `recursos.py`; re-renderizar o texto do HUD só quando o valor mudar. |
| **D4** | **Estruturas certas** | `collections.deque` para o corpo (inserção na cabeça em O(1)) + `set` de células ocupadas para colisão e sorteio de comida em O(1). |
| **D5** | **Sorteio de comida sem laço cego** | Sortear entre as células livres (`random.choice` de grade − ocupadas). Quando não houver célula livre, vitória (J7). |
| **D6** | **Assets otimizados** | Exportar sprites no tamanho de uso e comprimir PNGs; usar `.convert()` em imagens sem transparência (fundos) e `.convert_alpha()` só onde há alfa. Carregar tudo uma vez, depois de `set_mode`. |
| **D7** | **Medir antes de otimizar** | Mostrar FPS no modo de depuração; usar `cProfile` se aparecer queda. Otimizações como dirty rects só se a medição justificar. |

---

## 7. Qualidade, documentação e entrega

- **Testes** (`pytest`) para o domínio: movimento, crescimento, colisão com parede/corpo/obstáculo, buffer de direção (J1), sorteio de comida (D5), progressão de nível e modo sem bordas.
- **README da V2** atualizado: como instalar e rodar, controles, estrutura real de pastas, GIF de demonstração, seção "Novidades da V2", créditos de assets e sons.
- **Executável** com PyInstaller para Windows, publicado como *release* no GitHub, para quem quiser jogar sem instalar Python.
- **Commits pequenos e convencionais** (`feat:`, `fix:`, `refactor:`, `docs:`, já usados na V1) + entrada correspondente no `LOG.md`.

---

## 8. Decisões tomadas

Decididas em 2026-10-02.

### 8.1 Repositório

Repositório **novo** para a V2: <https://github.com/Joaofernandes-DEV/v2_jogoCobrinha>. A V1 fica na pasta local `Py_JogoDaCobrinha/` **só como referência** e está no `.gitignore`. O histórico da V1 continua no repositório original dela.

### 8.2 Grade e janela

| Item | Valor |
|------|-------|
| Janela | 800 × 600 px |
| Célula | 25 × 25 px |
| Área de jogo | 32 × 22 células = 800 × 550 px |
| HUD | faixa de 50 px no topo (y = 0–49); o campo começa em y = 50 |

A conversão é `pixel = (coluna * 25, 50 + linha * 25)`, e a lógica nunca trabalha em pixels (E2).

### 8.3 Arte: pixel art em estilo único

- **Toda a arte é refeita**; nenhum asset da V1 é reaproveitado.
- **Sprites em 25 × 25 px nativos** (escala 1:1, sem `transform.scale`) e **paleta limitada** (até 16 cores, definida em `config.py` e usada também pela UI).
- **Peças da cobra:** cabeça, corpo reto, corpo em curva, cauda e língua/olhos opcionais. As 4 direções são geradas por rotação de 90° (`pygame.transform.rotate`), que não distorce pixel art.
- **Fundo, paredes e HUD desenhados por código** com a paleta (xadrez de grama em dois tons, I5), sem imagens de tela cheia.
- **Fonte pixel** com licença livre em `assets/fontes/`: **VT323** (SIL OFL). A *Press Start 2P*, testada primeiro, foi descartada porque desenha as maiúsculas acentuadas encolhidas (Í parece "í") e Ó/Ô/Õ iguais às minúsculas, o que é inaceitável num jogo em português. Há um teste de regressão para isso.
- **Tela cheia** via `pygame.SCALED`, que escala a imagem inteira mantendo os pixels nítidos.
- **Como os assets foram feitos:** sprites e sons são gerados por código (`ferramentas/gerar_sprites.py` e `ferramentas/gerar_sons.py`, determinísticos). Os PNGs/WAVs resultantes são os assets oficiais e podem ser retocados no LibreSprite/Piskel ou trocados por sons do jsfxr.
- Créditos de fonte e sons listados no README.

### 8.4 Escopo de conteúdo da V2

Critério: entra o que torna o jogo **completo e polido** (um jogo pronto, não uma demo) sem abrir frentes que ficariam pela metade. O resto vai para o backlog da V3.

| Entra na V2 | Fica para a V3 |
|-------------|----------------|
| **J4** 3 níveis definidos como dados: 1 campo aberto, 2 com blocos internos, 3 labirinto | Editor de níveis |
| **J5** Uma comida especial: **fruta dourada** (+5 pontos, some em 5 s, chance de ~10% por comida) | Fruta de câmera lenta e outros power-ups |
| **J6** Top 5 de recordes local em JSON, com "novo recorde!" | Ranking online |
| **J8** Dois modos: **Clássico** (bordas matam) e **Sem bordas** (atravessa) | Modo contra o tempo |
| **J9** Leve aceleração dentro do nível | — |
| **I8** Efeitos sonoros retrô + 1 música de menu/jogo, com mudo (M) | Trilha diferente por nível |
| **I9** Opções: volumes, tela cheia, modo de jogo. Setas **e** WASD sempre funcionam | Remapeamento de teclas |
| **I10** "+1"/"+5" flutuante ao comer e cobra piscando ao morrer | Tremor de tela e partículas |
| **D1** Lógica em passo fixo + render a 60 FPS, **movimento discreto célula a célula** (fiel ao clássico e à pixel art) | Movimento interpolado/suave |
| **Seção 7** Testes, CI (GitHub Actions) e executável Windows (PyInstaller) anexado a uma *release* | Versão web (pygbag) |

### 8.5 Plataforma

**Python 3.11+** e **`pygame-ce`** (`import pygame` continua igual). As versões ficam fixadas no `pyproject.toml`.

---

## 9. Roteiro em fases

Cada fase deixa o jogo **jogável** ao final.

| Fase | Foco | Itens | Pronto quando… |
|------|------|-------|----------------|
| **0. Fundação** ✅ | Esqueleto do projeto | E3, E5, E7, E1 (mínimo), paleta e grade (8.2) | `python -m cobrinha` abre a janela 800 × 600 com HUD e grade 32 × 22 desenhados e fecha sem erro; lint e CI passando. |
| **1. Núcleo do jogo** ✅ | Domínio + estados | E1, E2, E4, E6, E8, D1–D5, J1, regra de vitória do J7 | Snake jogável com formas simples no lugar dos sprites, sem nenhum dos bugs B1–B7, com testes do domínio passando. |
| **2. Jogabilidade essencial** ✅ | Fluxo da partida | J2, J3, J10, `--nivel` (E8) + menu inicial simples | Pausa, níveis com progressão sem interrupção, contagem 3‑2‑1 e menu para começar. |
| **3. Interface** ✅ | Pixel art e som | I1–I8, D6 + tela de créditos | Menus navegáveis, HUD em faixa, sprites pixel art com curvas, sons. |
| **4. Conteúdo** ✅ | Variedade | J4, J5, J6, J8, J9, I9, I10, I11 (parcial) | Níveis distintos, recordes salvos, opções persistentes. |
| **5. Entrega** ✅ | Portfólio | Seção 7, I11 | README com GIF, CI verde, executável na *release* `v2.0.0`, LOG completo. |

**Prioridade se o tempo apertar:** Fases 0–2 são o mínimo para a V2 valer como nova versão (como a V2 é reescrita do zero, os bugs B1–B7 são eliminados pelo próprio desenho da Fase 1); a Fase 3 é o que mais muda a percepção de qualidade; a Fase 4 pode ser cortada item a item.
