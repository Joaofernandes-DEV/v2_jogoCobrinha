# Jogo da Cobrinha — V2 🐍

[![CI](https://github.com/Joaofernandes-DEV/v2_jogoCobrinha/actions/workflows/ci.yml/badge.svg)](https://github.com/Joaofernandes-DEV/v2_jogoCobrinha/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/Joaofernandes-DEV/v2_jogoCobrinha)](https://github.com/Joaofernandes-DEV/v2_jogoCobrinha/releases/latest)

Reescrita completa do [Jogo da Cobrinha (V1)](https://github.com/Joaofernandes-DEV/Py_JogoDaCobrinha), feito em Python + Pygame na disciplina de Computação Gráfica (UNIP).

![Demonstração: menu, contagem do nível 2, partida com a maçã dourada e os power-ups de câmera lenta e pontos em dobro, e fim de jogo](docs/demo.gif)

## Baixar e jogar (Windows)

1. Baixe o **`Cobrinha.exe`** da [última release](https://github.com/Joaofernandes-DEV/v2_jogoCobrinha/releases/latest).
2. Dê dois cliques. Não precisa instalar Python.
3. Se o Windows mostrar "O Windows protegeu o computador" (SmartScreen), clique em **Mais informações → Executar assim mesmo**. O aviso aparece porque o executável não tem assinatura digital paga.

## O que muda na V2

- Código modular: regras do jogo separadas da interface, com testes automatizados.
- Arte nova e coesa em **pixel art**, grade de 32 × 22 células e HUD próprio.
- Menus navegáveis por teclado e mouse, pausa, recordes, sons e dois modos de jogo.
- Correção dos bugs da V1 (fechamento com erro, grade desalinhada, meia-volta suicida etc.).

## Novidades da V3

A V3 (`v3.0.0` a `v3.2.0`) continua a partir da V2, com o mesmo nome e o mesmo movimento célula a célula. O executável da [última release](https://github.com/Joaofernandes-DEV/v2_jogoCobrinha/releases/latest) já traz as novidades abaixo.

**Power-ups:** às vezes um aparece depois de comer. Ele fica no campo por 7 segundos (pisca antes de sumir) e, ao ser pego, não dá pontos nem faz crescer, só aplica o efeito.

| Item | Power-up | Efeito |
|:----:|----------|--------|
| <img src="src/cobrinha/assets/imagens/power_camera_lenta.png" alt="Fruta azul com relógio"> | **Câmera lenta** | A cobra anda na metade da velocidade por 5 s, e o campo fica azulado. |
| <img src="src/cobrinha/assets/imagens/power_pontos_em_dobro.png" alt="Cereja dupla"> | **Pontos em dobro** | Por 8 s, cada maçã vale 2 pontos e a maçã dourada vale 10. A meta do nível continua contando 1 por maçã. |
| <img src="src/cobrinha/assets/imagens/power_encolher.png" alt="Cogumelo"> | **Encolher** | A cauda perde 3 segmentos na hora, sem a cobra ficar menor que o tamanho inicial. |

- Os efeitos ativos aparecem no HUD com os segundos restantes (ex.: `LENTO 4  X2 7`).
- Pegar de novo um efeito que já está ativo renova a duração. Os efeitos param na pausa e acabam ao trocar de nível.
- Sprites e som dos power-ups são gerados por código, como o resto dos assets (`ferramentas/gerar_sprites.py` e `ferramentas/gerar_sons.py`).

**Modo Contra o tempo:** feito pelo colaborador João Pedro Sinhorini Silva. Corrida de pontos contra um relógio de 60 s, em que cada maçã devolve segundos. Os power-ups também valem nesse modo. Veja as regras em [Como jogar](#como-jogar).

**Controle de PS5:** dá para jogar com o DualSense (USB ou Bluetooth), que vibra nos acontecimentos da partida e muda a cor da luz conforme o jogo. Veja os botões em [Controle de PS5 (DualSense)](#controle-de-ps5-dualsense).

**Modo Duelo (em desenvolvimento, ainda não está no executável):** de 2 a 4 pessoas no mesmo campo, cada uma com a sua cobra (verde, azul, amarela e vermelha), jogando pelo teclado (WASD e setas) ou pelo controle. Cada rodada vai até sobrar um; o primeiro a fazer 3 vitórias é o campeão. Os power-ups viram armas contra os adversários, e há uma variante com relógio. Veja as regras em [Como jogar](#como-jogar).

## Rodar pelo código-fonte

Pré-requisito: [Python 3.11+](https://www.python.org/downloads/).

```bash
git clone https://github.com/Joaofernandes-DEV/v2_jogoCobrinha.git
cd v2_jogoCobrinha
python -m venv .venv
```

Ative o ambiente virtual (Windows: `.venv\Scripts\activate`; Linux/macOS: `source .venv/bin/activate`), instale e rode:

```bash
pip install -e ".[dev]"
python -m cobrinha
```

### Controles

| Tecla | Ação |
|-------|------|
| Setas ou `W` `A` `S` `D` | Mover a cobra; navegar nos menus |
| `W` `A` `S` `D` / setas, no Duelo | Mover a cobra de quem entrou pelo lado esquerdo / direito do teclado |
| `←` `→` | Escolher o nível inicial no menu |
| `Enter` / `Espaço` / clique | Confirmar; pular a contagem 3-2-1 |
| Mouse | Escolher e clicar nas opções dos menus |
| `Esc` ou `P` | Pausar / continuar |
| `M` | Ligar / desligar o som |
| `Esc` no menu principal | Sair |

O jogo também pausa sozinho quando a janela perde o foco.

#### Controle de PS5 (DualSense)

Conecte o controle por cabo USB ou Bluetooth, antes ou depois de abrir o jogo. Outros controles reconhecidos pelo Windows (como o do Xbox) também funcionam, com os botões nas mesmas posições.

| Controle | Ação |
|----------|------|
| Direcional ou analógico esquerdo | Mover a cobra; navegar nos menus |
| ✕ | Confirmar; pular a contagem 3-2-1 |
| ◯ | Voltar; pausar durante a partida |
| Options | Pausar / continuar |
| Create | Ligar / desligar o som |

- **Vibração:** curta ao comer, média na maçã dourada, nos power-ups e ao concluir o nível, e forte ao bater ou quando o tempo acaba.
- **Luz do controle:** verde jogando, azul na câmera lenta, amarela com pontos em dobro e vermelha ao bater ou quando o relógio do Contra o tempo está acabando.
- Se o controle desconectar no meio da partida, o jogo pausa.
- **No Duelo**, cada controle é de um jogador: ele acende na cor da cobra dele (fica cinza quando ele é eliminado; os controles que não jogam ficam brancos) e só vibra com o que acontece com ele. Se o controle de um jogador desconectar, o duelo para até ele ser reconectado e apertar ✕.
- No menu principal, o ◯ não fecha o jogo (para sair, use a opção SAIR).

### Como jogar

Coma a quantidade de comidas da meta (barra no HUD) para concluir o nível. Os pontos se acumulam entre os níveis, e zerar o nível 3 (ou encher o campo) vence o jogo.

| Nível | Nome | Novidade |
|-------|------|----------|
| 1 | Campo aberto | Sem obstáculos |
| 2 | Pedras no caminho | Pedras espalhadas pelo campo |
| 3 | Labirinto | Paredes formando corredores |

- **A cobra acelera** um pouco a cada maçã, e cada nível começa mais rápido que o anterior.
- **Maçã dourada:** às vezes aparece depois de comer. Vale **+5 pontos**, faz crescer, não conta para a meta e **some em 5 segundos** (pisca antes de sumir).
- **Modos de jogo** (escolha no menu, com `←` `→`): **Clássico**, em que bater na borda perde; **Sem bordas**, em que a cobra atravessa a borda e sai do outro lado (pedras e o próprio corpo continuam valendo); e **Contra o tempo**, descrito abaixo.
- **Contra o tempo:** uma corrida de pontos no nível escolhido. O relógio começa em **60 s** e não há meta de comidas, então o nível não acaba ao comer. Cada maçã dá **+3 s** e a maçã dourada dá **+5 s** (o relógio nunca passa de 99 s). Abaixo de 10 s o relógio fica vermelho. Quando o tempo acaba, a partida termina em "Tempo esgotado!" e os pontos entram no ranking do modo; bater na borda, nas pedras ou no próprio corpo também encerra.
- **Duelo:** escolha DUELO no menu. Na tela **Quem joga?**, cada pessoa entra apertando `W` `A` `S` `D` (lado esquerdo do teclado), uma seta (lado direito) ou ✕ no controle; com 2 a 4 jogadores, `Enter` (ou o ✕ de quem já entrou) começa, e ◯ tira o controle da vaga. As cores seguem a ordem de chegada: verde, azul, amarela e vermelha. O mapa e a velocidade são os do nível escolhido em "Nível inicial". As cobras andam ao mesmo tempo, e cada maçã faz crescer e acelera o jogo para todos. Bater na borda, numa pedra, em si mesmo ou em outra cobra elimina, e a cobra eliminada pisca e some do campo. Se duas cabeças entram na mesma célula, ou trocam de lugar, as duas são eliminadas. Vence a rodada quem sobrar; se todos forem eliminados no mesmo passo, é empate.
  - **Rodadas:** entre uma rodada e outra, o placar mostra as vitórias de cada um (quadradinhos, também no HUD). Quem fizer **3 vitórias** é o campeão; empate não conta. "Reiniciar" (na pausa) e "Jogar de novo" (depois do campeão) começam outra disputa com os mesmos jogadores.
  - **Modo:** o item MODO do menu vale também no duelo. No **Clássico**, a borda elimina; no **Sem bordas**, a cobra atravessa; no **Contra o tempo**, cada rodada tem **60 s** (maçãs não dão tempo) e vence quem tiver **mais pontos** quando o tempo acabar (pontos iguais: empate). Quem é eliminado sai do campo, mas os pontos dele continuam valendo; a rodada só acaba antes se não sobrar ninguém ou se o último vivo já estiver na frente.
  - **Power-ups disputados:** a **câmera lenta** deixa os adversários na metade da velocidade por 5 s (e tira a lentidão de quem pegou); o **cogumelo** corta 3 segmentos da cauda dos adversários; os **pontos em dobro** valem por 8 s só para quem pegou e só aparecem no Contra o tempo. O HUD mostra quem está lento ou com pontos em dobro.
  - O duelo não entra nos recordes.
- **Power-ups (V3):** câmera lenta, pontos em dobro e encolher. Veja a tabela em [Novidades da V3](#novidades-da-v3).
- **Recordes:** os 5 melhores de cada modo ficam salvos, e os níveis alcançados ficam liberados no menu.
- **Opções:** volume dos efeitos e da música, tela cheia e efeitos visuais (desligue para tirar o pisca-pisca e os textos de pontos).
- **Música:** o menu tem a própria música, e cada fase tem uma diferente (dó maior alegre, ré menor sincopada, mi menor rápida). Ao bater, a música para na hora e só volta no menu.

Os dados ficam em `%APPDATA%\Cobrinha\dados.json` no Windows (ou `~/.local/share/cobrinha/` no Linux/macOS).

### Opções de linha de comando

```bash
python -m cobrinha --debug        # mostra FPS e tamanho da cobra
python -m cobrinha --semente 42   # repete exatamente a mesma sequência de comidas
python -m cobrinha --nivel 3      # pula o menu e começa direto no nível 3
python -m cobrinha --fechar-em 5  # fecha sozinho depois de 5 s (teste automático)
```

## Desenvolvimento

```bash
ruff check .            # lint
ruff format .           # formatação
pytest                  # testes (rodam sem abrir janela)
```

Sprites e sons são gerados por código. Para recriá-los (o resultado é sempre o mesmo):

```bash
python ferramentas/gerar_sprites.py   # PNGs 25 × 25 (com a cobra em 4 cores) em src/cobrinha/assets/imagens/
python ferramentas/gerar_sons.py      # WAVs em src/cobrinha/assets/sons/
```

Executável e GIF de demonstração (precisam de `pip install -e ".[ferramentas]"`):

```bash
python ferramentas/empacotar.py       # dist/Cobrinha.exe, já testado ao final
python ferramentas/gravar_demo.py     # docs/demo.gif, jogado por um piloto automático (com power-ups)
```

**Publicar uma versão:** basta criar e enviar uma tag (ex.: `git tag v3.2.1 && git push origin v3.2.1`). O workflow `release.yml` roda os testes no Windows, gera e testa o executável e cria a release com ele anexado.

O GitHub Actions roda lint e testes a cada push (Linux com Python 3.11–3.13 e Windows com 3.11).

## Estrutura

```plaintext
src/cobrinha/
├── __main__.py      # ponto de entrada (python -m cobrinha)
├── config.py        # grade, janela, FPS e paleta de cores
├── jogo.py          # loop principal e pilha de estados (telas)
├── recursos.py      # carregamento único de fontes e imagens
├── audio.py         # efeitos, música e mudo
├── controle.py      # controle de videogame: botões viram teclas, vibração e luz
├── entradas.py      # Duelo: de que lado do teclado ou de que controle vem cada jogador
├── assets/          # fonte, sprites (PNG) e sons (WAV)
├── dominio/         # regras puras, sem pygame (testáveis)
│   ├── grade.py     #   Posicao, Direcao e Grade
│   ├── cobra.py     #   corpo, movimento, crescimento e fila de direções
│   ├── comida.py    #   sorteio entre as células livres
│   ├── niveis.py    #   níveis como dados (velocidade, meta e mapa de pedras)
│   ├── progresso.py #   ranking por modo e níveis liberados
│   ├── power_ups.py #   tipos de power-up e duração dos efeitos
│   ├── partida.py   #   passo fixo, modos, colisões, fruta dourada, vitória e derrota
│   └── duelo.py     #   várias cobras no mesmo passo, colisões entre elas e vencedor
├── opcoes.py        # preferências do jogador
├── persistencia.py  # leitura/gravação do JSON de dados
├── estados/         # telas: menu, recordes, opções, créditos, contagem, jogo, quem joga, duelo, pausa, fim
│   └── navegacao.py #   mapa de todas as trocas de tela
└── ui/              # HUD, campo, sprites, menu, painéis, efeitos e texto
ferramentas/         # geradores de sprites e sons, empacotador e gravador do GIF
docs/                # GIF de demonstração e notas das releases
tests/               # pytest
```

## Documentos do projeto

| Arquivo | Conteúdo |
|---------|----------|
| [briefing_v2.md](briefing_v2.md) | Diagnóstico da V1, decisões e plano de melhorias em fases |
| [LOG.md](LOG.md) | Diário de bordo com todas as alterações, por data e horário |
| [docs/ebook/](docs/ebook/) | Ebook didático (PDF, ABNT) sobre os conceitos de Computação Gráfica aplicados no jogo |

## Tecnologias

Python 3.11+ · [pygame-ce](https://pyga.me/) · pytest · ruff · GitHub Actions

## Créditos

- **V2:** João Vitor Fernandes e, como colaborador, João Pedro Sinhorini Silva.
- **V1 (2025), Computação Gráfica:** João Vitor Fernandes, João Pedro Sinhorini Silva, Vitor Barssoti de Souza e Alex Barbosa Lourenço.
- **Fonte:** [VT323](https://fonts.google.com/specimen/VT323), de Peter Hull, sob a [SIL Open Font License 1.1](src/cobrinha/assets/fontes/OFL.txt).
- **Sprites e sons:** gerados por código neste repositório.

## Licença

Código sob a [MIT](LICENSE) © João Vitor Fernandes. A fonte VT323 mantém a própria licença (SIL OFL 1.1).
