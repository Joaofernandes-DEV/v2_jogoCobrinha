# O projeto: da V1 à V3

Antes de entrar nos conceitos, vale conhecer o objeto de estudo e a sua história. O Jogo da Cobrinha passou por três versões, e várias decisões técnicas discutidas nos próximos capítulos só fazem sentido quando se sabe qual problema da versão anterior elas resolveram. As fontes deste capítulo são os documentos do próprio repositório: o `briefing_v2.md`, com o diagnóstico da V1 e o plano da V2, e o `LOG.md`, o diário de bordo com todas as mudanças, em ordem cronológica, com data, horário e motivo. A @fig:linha-do-tempo resume essa trajetória.

::: figura linha-do-tempo
Linha do tempo do projeto, da V1 à release v3.1.0
Fonte: elaborada pelo autor (2026), com base no `LOG.md` e nos *pull requests* do repositório.
:::

## A V1 (2025): o protótipo da disciplina

A primeira versão foi feita em grupo, em 2025, para a disciplina de Computação Gráfica, por João Vitor Fernandes, João Pedro Sinhorini Silva, Vitor Barssoti de Souza e Alex Barbosa Lourenço. Era um Snake funcional em Pygame, com três níveis de velocidade, telas de transição desenhadas no Canva e sprites direcionais para a cobra, tudo num único arquivo de 348 linhas.

O briefing da V2 reconhece que a V1 cumpria o objetivo acadêmico, mas registra problemas que reaparecerão neste ebook como contraexemplos. O @qua:bugs-v1 resume os principais.

::: quadro #bugs-v1
Problemas da V1 diagnosticados no briefing da V2
Fonte: adaptado de `briefing_v2.md`, seções 2.1 a 2.5.
| Código | Problema | Conceito relacionado (capítulo) |
|---|---|---|
| B1, B5 | `pygame.quit()` chamado e o desenho continuando depois; o jogo fechava com erro | laço de jogo (5) |
| B2 | Cobra nascendo em `x = 400` (não múltiplo de 30) e comida em múltiplos de 30: grade desalinhada | sistemas de coordenadas (4) |
| B3 | Direção validada contra a direção atual: duas teclas rápidas causavam meia-volta e morte | modelo e entrada (12) |
| B7 | Laço infinito ao sortear a comida com o campo cheio | colisão em grade (12) |
| — | Sprites de até 840 × 462 px esticados para 30 × 30 e fundo de 319 × 161 ampliado para 800 × 600, borrado | escala e pixel art (7, 8) |
| — | Comida em JPG, sem transparência: um quadrado de fundo aparecia em volta | canal alfa (10) |
| — | Lógica e desenho na mesma taxa (8 a 16 quadros por segundo) e menus sem limite de quadros, com 100% de CPU | passo de tempo fixo (5) |
:::

## A V2: reescrita completa

A V2 foi uma reescrita do zero feita por João Vitor Fernandes, planejada no briefing em seis fases (0 a 5), cada uma terminando com o jogo jogável. O diário de bordo registra todas elas em 2 de outubro de 2026, da fundação (08:58) à publicação da release v2.0.0 (11:43). As decisões centrais, numeradas no briefing, foram:

- **Grade lógica em células (E2)**: a cobra e a comida guardam `(coluna, linha)`, e a conversão para pixels acontece só no desenho. A janela tem 800 × 600 px: 32 × 22 células de 25 px mais uma faixa de 50 px para o HUD (capítulo 4).
- **Máquina de estados com um único laço (E1)**: cada tela é um objeto com `tratar_evento`, `atualizar` e `desenhar`, e `pygame.quit()` aparece em um único lugar (capítulos 5 e 6).
- **Lógica em passo fixo e desenho a 60 FPS (D1)**: a cobra anda num ritmo próprio, independente da taxa de quadros, e continua se movendo célula a célula, fiel ao clássico (capítulo 5).
- **Domínio sem pygame (E4)**: as regras ficam em `src/cobrinha/dominio/` e podem ser testadas sem abrir janela (capítulo 12).
- **Pixel art em 25 × 25 px nativos, paleta de até 16 cores, peças giradas em múltiplos de 90° e tela cheia com `pygame.SCALED`** (seção 8.3 do briefing; capítulos 7, 8 e 9).

A V2 também trouxe som sintetizado por código, recordes salvos em disco, três níveis com obstáculos, a fruta dourada, os modos Clássico e Sem bordas, testes automatizados (190 na v2.0.0), integração contínua no GitHub Actions e um executável para Windows. A @fig:captura-menu mostra o menu principal da versão atual.

::: figura captura-menu
Menu principal do jogo, com título e cobra decorativa desenhados com os próprios sprites
Fonte: captura gerada pelo autor (2026) com `docs/ebook/capturas.py`.
largura: 65%
:::

## A V3: power-ups, uma tentativa revertida e o modo Contra o tempo

A V3 começou na mesma noite. O primeiro item do backlog foi o **movimento interpolado**: em vez de pular de célula em célula, cada segmento da cobra deslizaria entre as células ao longo do intervalo de cada passo (*pull request* 2). Onze minutos depois entraram os **power-ups** (câmera lenta, pontos em dobro e encolher; *pull request* 3). Às 23:07, depois de jogar com o movimento suave, o autor decidiu voltar ao movimento discreto, e a remoção foi feita como um *pull request* próprio (4), para que o histórico registrasse a tentativa e a volta. Esse episódio é o estudo de caso do capítulo 11.

A release v3.0.0 saiu em 3 de outubro, e a v3.1.0, no mesmo dia, trouxe o modo **Contra o tempo**, implementado pelo colaborador João Pedro Sinhorini Silva: um relógio de 60 s em que cada maçã devolve segundos (*pull request* 8). O patch chegou sobre a v2.0.0 e foi integrado à V3 resolvendo conflitos com os power-ups, como descreve o diário de bordo.

## A arquitetura do código

A @fig:diagrama-arquitetura mostra como o código está dividido. A separação mais importante é horizontal: tudo o que está em `dominio/` é Python puro, sem nenhum `import pygame`; o resto (telas, desenho, carregamento de recursos e áudio) depende da biblioteca.

::: figura diagrama-arquitetura
Arquitetura do Jogo da Cobrinha: módulos que dependem do pygame e o domínio puro
Fonte: elaborada pelo autor (2026), com base na estrutura de `src/cobrinha/`.
:::

Cada tela do jogo (menu, contagem, partida, pausa, fim de partida, recordes, opções, créditos) é uma subclasse de `Estado`, cujo contrato aparece no @cod:estado-base. O laço principal chama esses três métodos a cada quadro, e é essa regularidade que permite tratar todas as telas da mesma forma no pipeline de desenho (capítulo 6).

::: codigo #estado-base src/cobrinha/estados/base.py 14-29
Contrato comum a todas as telas (`Estado`)
:::

O padrão é conhecido como *State* na literatura de projeto orientado a objetos (Gamma *et al.*, 1994) e é recomendado por Nystrom (2014) para organizar as telas e os modos de um jogo. No Jogo da Cobrinha, ele substituiu os laços `while True` aninhados da V1, em que cada tela tinha o próprio laço e devolvia valores de tipos misturados para indicar a próxima tela, origem dos erros B1 e B5.

<div class="caixa" markdown="1">
<p class="titulo-caixa">Para ir além</p>

O arquivo `src/cobrinha/estados/navegacao.py` concentra todas as trocas de tela e traz no topo um diagrama em texto do fluxo. Compare esse diagrama com a @fig:fluxo-estados, no capítulo 6.
</div>
