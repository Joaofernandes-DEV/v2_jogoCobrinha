# Sistemas de coordenadas

Todo desenho começa com uma pergunta: *onde*? Em CG, essa pergunta tem sempre mais de uma resposta, porque o mesmo objeto pode ser descrito em vários sistemas de coordenadas. Hearn, Baker e Carithers (2011) distinguem as **coordenadas de mundo**, em que a cena é modelada, das **coordenadas de dispositivo**, os pixels da tela, e chamam de transformação de visualização (*window-to-viewport*) a função que leva de um sistema ao outro. Este capítulo mostra que o Jogo da Cobrinha tem exatamente essa estrutura, em escala pequena: um mundo de células e uma tela de pixels.

## Coordenadas de tela

Nas bibliotecas raster, incluindo o pygame-ce e a SDL, a origem (0, 0) fica no **canto superior esquerdo** da janela: o eixo *x* cresce para a direita e o eixo *y* cresce **para baixo**. Isso é o contrário da convenção da matemática escolar, e herda a forma como os monitores de tubo varriam a tela, linha a linha, de cima para baixo. Um pixel na posição (*x*, *y*) está *x* colunas à direita e *y* linhas abaixo da origem.

Essa inversão do eixo *y* aparece no próprio domínio do jogo. O @cod:direcao mostra que "para cima" é o deslocamento (0, −1): subir na tela é diminuir a linha.

::: codigo #direcao src/cobrinha/dominio/grade.py 13-35
Direções e posições da grade, em células (`dominio/grade.py`)
:::

## O mundo do jogo: uma grade de células

A decisão E2 do briefing estabelece que a lógica do jogo nunca trabalha em pixels. A cobra, a comida, as pedras e os power-ups têm posições do tipo `Posicao(coluna, linha)`, com coluna entre 0 e 31 e linha entre 0 e 21. Nesse mundo, mover a cobra é somar 1 a uma coordenada inteira, e saber se ela bateu é comparar tuplas. Não há frações de pixel, arredondamentos nem a possibilidade de dois objetos ficarem "meio desalinhados".

As medidas da janela, por sua vez, derivam da grade, e não o contrário. O @cod:config-grade mostra como a configuração define primeiro a célula, as colunas e as linhas, e calcula a largura e a altura da janela a partir delas.

::: codigo #config-grade src/cobrinha/config.py 13-21
Tamanho da janela derivado da grade (`config.py`)
:::

Com 32 colunas de 25 px, a largura é 32 × 25 = 800 px; com 22 linhas e o HUD de 50 px, a altura é 50 + 22 × 25 = 600 px. Mudar o tamanho da célula ou o número de linhas recalcula a janela inteira de forma consistente.

## A transformação de célula para pixel

A ponte entre o mundo e a tela é a função `celula_para_pixel`, no @cod:celula-pixel. Ela devolve o canto superior esquerdo da célula na janela.

::: codigo #celula-pixel src/cobrinha/ui/campo.py 15-17
Conversão de célula para pixel, com o deslocamento do HUD
:::

Escrita como fórmula, sendo *T* = 25 px o tamanho da célula e *h* = 50 px a altura do HUD:

<p class="formula">x = T · coluna   e   y = h + T · linha</p>

É uma **transformação afim**: uma escala uniforme por *T* seguida de uma translação de (0, *h*). Em coordenadas homogêneas, que os livros de CG usam para escrever translações também como produto de matrizes (Hughes *et al.*, 2014; Marschner; Shirley, 2021), ela fica:

<pre>
| x |   | 25   0    0 |   | coluna |
| y | = |  0  25   50 | · | linha  |
| 1 |   |  0   0    1 |   |   1    |
</pre>

A @fig:diagrama-coordenadas ilustra a conversão para a célula (4, 3), que vai parar no pixel (100, 125).

::: figura diagrama-coordenadas
Coordenadas de tela do jogo: origem no canto superior esquerdo, HUD de 50 px e a conversão da célula (4, 3) para o pixel (100, 125)
Fonte: elaborada pelo autor (2026) com `docs/ebook/figuras.py`.
:::

Como toda a conversão está em uma função, mover o HUD para baixo, ou acrescentar uma borda em volta do campo, exige mudar uma única linha. É também por isso que o fundo do campo é desenhado numa superfície própria, com origem no topo do campo (sem o HUD), e copiado para a janela na posição (0, 50) (capítulo 6).

## Contraexemplo: o bug B2 da V1

A V1 não tinha essa separação. A cobra nascia em `x = 400` px, que não é múltiplo do tamanho de célula de 30 px usado na época (400 = 13 × 30 + 10), enquanto a comida nascia em múltiplos de 30. Além disso, 800 / 30 ≈ 26,67: a janela não comportava um número inteiro de células, e sobrava uma faixa de 20 px na borda direita. O resultado, registrado no briefing como B2, era uma cobra 10 px deslocada da comida, que "comia" por sobreposição parcial, e uma colisão inconsistente com a borda direita.

O problema não era de aritmética, mas de modelo: a posição da cobra existia em pixels e podia assumir qualquer valor. Na V2, a grade é a única fonte de verdade, e um desalinhamento desse tipo se torna impossível por construção.

## Escalas além da janela: SCALED e o mouse

Há ainda um terceiro sistema de coordenadas no jogo, o da janela física. Com `pygame.SCALED`, o jogo desenha sempre numa superfície de 800 × 600, mas a janela pode estar ampliada ou em tela cheia. A documentação do pygame-ce descreve exatamente esse comportamento: o jogo "pensa" que a janela tem o tamanho original, mas ela pode ser maior, e os eventos de mouse são convertidos automaticamente (Pygame-ce Developers, c2023). Por isso os menus que respondem ao mouse (`ui/menu.py`) comparam a posição do clique com os retângulos dos itens sem nenhuma conta extra: a SDL já desfez a escala.

<div class="caixa" markdown="1">
<p class="titulo-caixa">Resumo do capítulo</p>

O jogo tem três sistemas de coordenadas: células (o mundo lógico, usado pelas regras), pixels lógicos de 800 × 600 (onde tudo é desenhado) e pixels físicos da janela (cuidados pela SDL). As conversões entre eles ficam em um único lugar cada: `celula_para_pixel` e a opção `SCALED`.
</div>
