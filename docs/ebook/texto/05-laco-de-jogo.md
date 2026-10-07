# Laço de jogo e passo de tempo fixo

Um programa comum espera o usuário: lê um comando, executa e espera o próximo. Um jogo não pode esperar. Mesmo sem nenhuma tecla pressionada, a cobra continua andando, a comida continua flutuando e o relógio do modo Contra o tempo continua correndo. Nystrom (2014) descreve a solução com o padrão *Game Loop*: um laço que, a cada volta, processa a entrada do usuário sem bloquear, atualiza o estado do jogo e desenha o resultado, controlando a passagem do tempo. Este capítulo mostra esse laço no Jogo da Cobrinha e a decisão D1 do briefing: separar o ritmo da lógica do ritmo do desenho.

## O laço principal

O laço do jogo está no método `Jogo.executar`, no @cod:executar. É o único `while` que roda durante toda a execução: todas as telas são atendidas por ele, por meio da pilha de estados (capítulo 6).

::: codigo #executar src/cobrinha/jogo.py 92-105
Laço principal do jogo (`Jogo.executar`)
:::

Cada volta tem quatro etapas, que a @fig:fluxo-laco-principal mostra como fluxograma:

1. **Medir o tempo**: `relogio.tick(FPS)` espera o necessário para não passar de 60 quadros por segundo e devolve quantos milissegundos se passaram desde a volta anterior. Dividido por 1000, esse valor vira `dt`, em segundos.
2. **Processar eventos**: teclas, mouse, perda de foco e o pedido de fechar a janela são lidos da fila da SDL e entregues à tela do topo da pilha.
3. **Atualizar**: a tela do topo avança sua lógica em `dt` segundos.
4. **Desenhar e exibir**: o quadro é montado no buffer de trás e mostrado com `flip()` (capítulo 3).

::: figura fluxo-laco-principal
Fluxograma do laço principal: eventos, atualização, desenho e `flip()`
Fonte: elaborada pelos autores (2026) com base em `src/cobrinha/jogo.py`.
:::

Dois detalhes do código corrigem diretamente bugs da V1. O bloco `try ... finally` garante que `pygame.quit()` seja chamado em um único ponto, depois que o laço termina, por qualquer motivo (B1 e B5). E o `clock.tick` vale para todas as telas, inclusive os menus, que na V1 rodavam em laços próprios sem limite de quadros e ocupavam 100% de um núcleo da CPU enquanto o jogador lia as opções (item D2 do briefing).

## Duas velocidades diferentes

Na V1, o desenho e a lógica rodavam no mesmo ritmo: entre 8 e 16 quadros por segundo, conforme o nível. A animação ficava "aos trancos" e o teclado só era lido a cada passo da cobra. A tentação oposta seria mover a cobra uma célula por quadro a 60 FPS, mas aí a velocidade do jogo dependeria do computador: numa máquina lenta, que só conseguisse 30 quadros por segundo, a cobra andaria na metade da velocidade.

Fiedler (2004) discute as alternativas para avançar uma simulação no tempo e defende a seguinte: o programa desenha tão rápido quanto puder (ou quanto o limite de quadros permitir), mas a simulação avança em **passos de tamanho fixo**. Um **acumulador** guarda o tempo real que ainda não foi "consumido" pela simulação; a cada quadro, o tempo do quadro entra no acumulador, e enquanto houver tempo suficiente para um passo inteiro, um passo é executado e seu tempo é descontado.

## O acumulador na partida

O @cod:atualizar-partida é a implementação dessa ideia no domínio do jogo, sem nenhuma dependência do pygame.

::: codigo #atualizar-partida src/cobrinha/dominio/partida.py 141-159
Passo de tempo fixo com acumulador (`Partida.atualizar`)
:::

O intervalo de um passo é o inverso da velocidade da cobra, `1 / passos_por_segundo`. No nível 1, que começa com 8 passos por segundo, o intervalo é de 0,125 s, enquanto um quadro a 60 FPS dura cerca de 0,0167 s. Por isso, na maioria dos quadros o laço `while` da linha 153 não executa nenhum passo: o acumulador só cresce. A cada sete ou oito quadros, ele passa do intervalo, um passo é executado, e o excesso fica guardado para o próximo. A @fig:grafico-acumulador simula esse comportamento com os valores reais do jogo e mostra o "dente de serra" característico do acumulador.

::: figura grafico-acumulador
Valor do acumulador ao longo de 0,6 s, com quadros a 60 FPS e passos a cada 0,125 s
Fonte: elaborada pelos autores (2026), simulando a regra do @cod:atualizar-partida.
:::

Note que o acumulador às vezes passa um pouco do intervalo antes de o passo acontecer (por exemplo, 8 × 1/60 ≈ 0,133 s), porque o tempo só é verificado uma vez por quadro. O excesso não se perde: ele fica no acumulador e antecipa o passo seguinte. Em média, a cobra anda exatamente 8 células por segundo, qualquer que seja a taxa de quadros.

A @fig:fluxo-passo-fixo mostra o método inteiro como fluxograma, incluindo o envelhecimento dos itens temporários (fruta dourada e power-ups) e o relógio do modo Contra o tempo.

::: figura fluxo-passo-fixo
Fluxograma do passo de tempo fixo em `Partida.atualizar`
Fonte: elaborada pelos autores (2026) com base em `src/cobrinha/dominio/partida.py`.
:::

## O teto de passos e a "espiral da morte"

Fiedler (2004) aponta um risco da técnica: se a simulação de um passo demorar mais do que o tempo que ele representa, o programa nunca alcança o relógio, e cada quadro precisa executar mais passos que o anterior, numa "espiral da morte". No Jogo da Cobrinha, um passo é barato, mas existe um caso parecido: quando o usuário arrasta a janela no Windows, o laço fica parado por um tempo, e o `dt` seguinte chega enorme. Sem proteção, a cobra executaria dezenas de passos de uma vez e apareceria "teleportada", provavelmente já morta.

As linhas 150 e 151 resolvem isso limitando o acumulador a três intervalos (`MAX_PASSOS_POR_QUADRO`, em `config.py`). O jogo prefere perder tempo de simulação a mostrar um salto que o jogador não teve chance de ver. O relógio do modo Contra o tempo segue a mesma regra (linhas 156 a 158): ele desconta no máximo o mesmo limite, de modo que um travamento não "rouba" segundos do jogador. A regra está descrita no diário de bordo, na entrada do modo Contra o tempo.

## Velocidade variável sem mudar o laço

Como a lógica só conhece o intervalo do passo, mudar a velocidade da cobra é só mudar `passos_por_segundo`. O @cod:velocidade mostra que três regras de jogabilidade (velocidade do nível, aceleração a cada comida e o power-up de câmera lenta) se reduzem a uma conta.

::: codigo #velocidade src/cobrinha/dominio/partida.py 112-123
Velocidade da cobra: nível, aceleração e câmera lenta (`Partida.passos_por_segundo`)
:::

A câmera lenta, por exemplo, multiplica a velocidade por 0,5: o intervalo dobra e o acumulador leva o dobro de quadros para completar um passo. Nada no laço principal, no desenho ou na taxa de quadros precisa saber que o jogo está em câmera lenta.

## Passo fixo e testes

Um efeito colateral valioso do passo fixo é a **reprodutibilidade**. Fiedler (2004) observa que ele permite repetir exatamente a mesma simulação de uma execução para outra. Os testes do projeto exploram isso: em `tests/test_partida.py`, partidas inteiras são simuladas chamando `atualizar` com valores de `dt` escolhidos pelo teste, sem janela e sem esperar o tempo real passar, e o gerador de números aleatórios recebe uma semente fixa. O GIF de demonstração do README é gravado da mesma forma: o jogo roda "de verdade", mas o tempo é controlado pelo script de gravação.

<div class="caixa" markdown="1">
<p class="titulo-caixa">Para ir além</p>

O artigo de Fiedler (2004) termina com uma etapa que o Jogo da Cobrinha não usa: **interpolar** o desenho entre os dois últimos estados da simulação, usando a fração do passo que já passou. O capítulo 11 conta como essa técnica foi implementada na V3 e por que ela foi removida.
</div>
