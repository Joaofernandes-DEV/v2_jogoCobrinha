# Pipeline de desenho 2D

Em CG 3D, *pipeline* é a sequência de etapas que leva uma cena (vértices, triângulos, luzes e câmera) até os pixels da tela (Angel; Shreiner, 2020). Em um jogo 2D raster, o pipeline é bem mais curto, mas a ideia é a mesma: uma sequência fixa de operações, sempre na mesma ordem, que transforma o estado do jogo em um quadro. Este capítulo descreve essa sequência no Jogo da Cobrinha e os dois conceitos que a sustentam: o **algoritmo do pintor** e a operação de **blit**.

## O algoritmo do pintor

Quando vários objetos ocupam o mesmo lugar da tela, é preciso decidir qual deles aparece. A solução mais antiga é a do pintor de quadros: pintar primeiro o que está mais longe e por último o que está mais perto, deixando que cada camada cubra as anteriores. Hearn, Baker e Carithers (2011) apresentam esse método, chamado de **algoritmo do pintor** (*painter's algorithm*), entre as técnicas de determinação de superfícies visíveis: os objetos são ordenados por profundidade e desenhados do fundo para a frente.

Em 3D, ordenar por profundidade pode ser difícil, porque dois polígonos podem se cruzar ou se sobrepor de forma cíclica. Em um jogo 2D, a "profundidade" é uma decisão de projeto, e a ordem é fixa: o fundo vem antes dos objetos, que vêm antes da interface. O que importa é que essa ordem seja explícita e respeitada em todo quadro.

## Blit: copiar blocos de pixels

A operação básica do pipeline 2D é o *blit* (de *bit block transfer*): copiar um retângulo de pixels de uma superfície para outra, numa posição dada. No pygame-ce, `destino.blit(origem, posicao)` faz essa cópia e, quando a origem tem canal alfa, combina as cores com a do destino em vez de simplesmente substituí-las (Pygame-ce Developers, c2023). O capítulo 10 trata dessa combinação; aqui basta saber que cada `blit` é uma camada de tinta sobre o quadro.

## A ordem de pintura de uma partida

O @cod:desenhar-jogando é o método que desenha a tela de jogo. Lido de cima para baixo, ele é a própria lista de camadas, da mais funda para a mais próxima.

::: codigo #desenhar-jogando 270f2fc:src/cobrinha/estados/jogando.py 183-203
Ordem de pintura da partida (`EstadoJogando.desenhar`)
:::

1. **HUD** (linha 183): a faixa de 50 px no topo, com pontos, nível, recorde e efeitos ativos.
2. **Fundo do campo** (linha 184): o xadrez de grama e as pedras, copiados de uma só vez.
3. **Véu azul** (linhas 185 a 187): só durante a câmera lenta, com transparência (capítulo 10).
4. **Itens** (linhas 188 a 198): maçã, maçã dourada e power-up, cada um com sua animação (capítulo 11).
5. **Cobra** (linhas 199 e 200), que pisca durante a animação de morte.
6. **Textos flutuantes** (linha 201): o "+1" ou "X2!" que sobe e some.
7. **Informações de depuração** (linhas 202 e 203), só com a opção `--debug`.

A ordem tem consequências visíveis. A cobra é desenhada depois dos itens, então, se a maçã "flutuar" 1 px para dentro da célula vizinha, a cobra a cobre. Os textos flutuantes vêm depois da cobra, para nunca ficarem escondidos sob o corpo, como se vê no "+1" da @fig:captura-jogando, no capítulo 3.

A própria cobra também segue o algoritmo do pintor internamente. O @cod:desenhar-cobra percorre as peças da cauda para a cabeça, com `reversed`, para que a cabeça seja sempre a última a ser pintada.

::: codigo #desenhar-cobra 270f2fc:src/cobrinha/ui/pecas.py 130-133
Peças da cobra desenhadas da cauda para a cabeça
:::

Com o movimento célula a célula, as peças quase não se sobrepõem, porque cada uma ocupa a própria célula. A regra fazia diferença na versão com movimento interpolado (capítulo 11), em que segmentos vizinhos deslizavam e se cobriam parcialmente, e continua garantindo que a cabeça, a peça mais importante para o jogador, nunca fique escondida.

## Pré-renderização: o fundo desenhado uma vez

O fundo do campo tem 704 células (32 × 22), cada uma pintada com uma de duas cores, e as pedras de cada nível são dezenas de sprites. Nada disso muda durante o nível. Em vez de repetir esse trabalho a cada quadro, o jogo o faz uma única vez, ao criar a tela da partida, numa superfície própria (@cod:fundo-campo e linhas 79 e 80 do `jogando.py`). Depois, cada quadro só precisa de um `blit` do fundo pronto.

::: codigo #fundo-campo src/cobrinha/ui/campo.py 20-28
Fundo em xadrez pré-renderizado uma vez (`criar_fundo_campo`)
:::

Essa técnica, conhecida como **pré-renderização** ou *cache* de camada, troca memória por tempo: o fundo ocupa 800 × 550 pixels a mais na memória, mas o custo de desenhá-lo por quadro passa de centenas de operações para uma. Na V1, o fundo era uma imagem de 319 × 161 px ampliada a cada quadro para 800 × 600, o que além de custar caro a deixava borrada (briefing, seção 2.3).

A economia cresce com o número de pedras. No nível 3, "Labirinto" (@fig:captura-labirinto), as paredes formam corredores com dezenas de blocos, todos pintados uma única vez no início do nível.

::: figura captura-labirinto
Nível 3, "Labirinto": as pedras fazem parte do fundo pré-renderizado
Fonte: captura de tela do jogo, elaborada pelos autores (2026).
largura: 65%
:::

O xadrez em si tem uma função de interface, registrada no item I5 do briefing: as duas cores alternadas por célula, definidas pela paridade de `coluna + linha`, mostram a grade ao jogador sem precisar de linhas.

## Telas empilhadas

O pipeline não termina na tela de jogo. A pausa, a contagem 3-2-1, a tela de nível concluído e a de fim de partida são desenhadas **por cima** da partida congelada. Isso é possível porque o jogo guarda as telas numa pilha: `empilhar` põe uma tela nova no topo, `desempilhar` a retira, e `trocar_estado` esvazia a pilha e começa de novo (`jogo.py`, linhas 74 a 86). A @fig:fluxo-estados mostra todas as transições entre telas.

::: figura fluxo-estados
Telas do jogo e as transições entre elas; em lilás, as telas empilhadas sobre a partida
Fonte: elaborada pelos autores (2026) com base em `src/cobrinha/estados/navegacao.py`.
:::

Na hora de desenhar, `Jogo._desenhar` (@cod:desenhar, no capítulo 3) percorre a pilha **de baixo para cima**. Só a tela do topo recebe eventos e é atualizada, mas todas são pintadas. É o algoritmo do pintor aplicado a telas inteiras: a partida é pintada primeiro e a pausa, por último, como mostra a @fig:captura-pausa.

::: figura captura-pausa
Tela de pausa empilhada sobre a partida congelada: o véu escuro deixa o campo visível ao fundo
Fonte: captura de tela do jogo, elaborada pelos autores (2026).
largura: 65%
:::

O @cod:desenhar-pausa mostra que a tela de pausa não precisa redesenhar nada da partida: ela só pinta um véu escuro semitransparente sobre o que já está no quadro e escreve o menu.

::: codigo #desenhar-pausa 270f2fc:src/cobrinha/estados/pausa.py 67-79
A pausa pinta só o véu e o menu (`EstadoPausa.desenhar`)
:::

## O quadro completo

A @fig:fluxo-pipeline-quadro junta tudo: o fluxograma à esquerda segue a ordem das chamadas, e a ilustração à direita mostra as camadas empilhadas na ordem em que são pintadas.

::: figura fluxo-pipeline-quadro
Pipeline de desenho de um quadro durante a pausa: etapas (à esquerda) e camadas (à direita)
Fonte: elaborada pelos autores (2026) com base em `jogo.py`, `estados/jogando.py` e `estados/pausa.py`.
:::

## Redesenhar tudo a cada quadro?

O jogo limpa e redesenha a tela inteira a cada quadro, mesmo quando quase nada mudou. Uma alternativa clássica é atualizar só os retângulos que mudaram (*dirty rectangles*), técnica que o pygame suporta com `pygame.display.update(retangulos)`. O briefing a deixa de propósito como último recurso (item D7, "medir antes de otimizar"): com 480 000 pixels, uma dúzia de `blit` por quadro e cópias feitas em C pela SDL, o redesenho completo cabe com folga nos 16,7 ms de um quadro a 60 FPS, e o código fica muito mais simples. A opção `--debug` mostra o FPS real no canto da tela, justamente para que essa decisão possa ser verificada.
