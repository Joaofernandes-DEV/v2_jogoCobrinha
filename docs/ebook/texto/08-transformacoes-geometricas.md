# Transformações geométricas

As transformações geométricas (translação, rotação e escala) são o vocabulário básico da CG: com elas, um mesmo modelo pode ser posicionado, orientado e dimensionado de muitas formas, sem ser redesenhado. Hughes *et al.* (2014) e Marschner e Shirley (2021) dedicam capítulos inteiros a elas, porque são a base de todo o pipeline gráfico. Este capítulo apresenta as três transformações no plano e mostra duas delas aplicadas a imagens raster no jogo: a rotação das peças da cobra e a escala da tela cheia.

## As transformações no plano

Um ponto do plano é um par (*x*, *y*). As transformações mais simples são:

- **Translação** por (*t*<sub>x</sub>, *t*<sub>y</sub>): (*x*, *y*) → (*x* + *t*<sub>x</sub>, *y* + *t*<sub>y</sub>).
- **Escala** por (*s*<sub>x</sub>, *s*<sub>y</sub>), em relação à origem: (*x*, *y*) → (*s*<sub>x</sub> *x*, *s*<sub>y</sub> *y*).
- **Rotação** por um ângulo *θ* em torno da origem: (*x*, *y*) → (*x* cos *θ* − *y* sen *θ*, *x* sen *θ* + *y* cos *θ*).

A escala e a rotação são **transformações lineares** e podem ser escritas como multiplicação por uma matriz 2 × 2. A translação não é linear, mas, com **coordenadas homogêneas**, em que o ponto vira (*x*, *y*, 1), as três passam a ser matrizes 3 × 3 e podem ser compostas por multiplicação (Hughes *et al.*, 2014; Marschner; Shirley, 2021). O capítulo 4 já mostrou um exemplo: a conversão de célula para pixel é uma escala por 25 seguida de uma translação de 50 px no eixo *y*.

Há um cuidado com o sentido da rotação. A fórmula acima gira no sentido anti-horário quando o eixo *y* aponta para cima, como na matemática. Na tela, com *y* para baixo (capítulo 4), a mesma fórmula gira no sentido horário. A função `pygame.transform.rotate` do pygame-ce gira no sentido anti-horário **como visto na tela** (Pygame-ce Developers, c2023). Em coordenadas de tela, uma rotação de 90° nesse sentido leva a direção "direita", (1, 0), para "cima", (0, −1), e corresponde à matriz:

<pre>
| x' |   |  0   1 |   | x |
| y' | = | -1   0 | · | y |
</pre>

## Rotacionar imagens raster

Rotacionar um modelo geométrico é simples: aplica-se a matriz a cada vértice. Rotacionar uma **imagem raster** é outra história. Cada pixel da imagem nova tem de buscar sua cor na imagem original, na posição obtida pela rotação inversa, e essa posição em geral cai **entre** pixels. É preciso então reconstruir a imagem entre as amostras, por exemplo copiando a amostra mais próxima ou interpolando as vizinhas (Smith, 1995; Marschner; Shirley, 2021). Para ângulos quaisquer, a imagem também cresce, porque o retângulo girado precisa de uma caixa maior. A documentação do pygame-ce registra as duas coisas: fora dos múltiplos de 90°, a rotação aumenta a superfície e preenche as sobras com transparência, e o resultado não é filtrado (Pygame-ce Developers, c2023).

Os múltiplos de 90° são um caso especial. A matriz da rotação de 90° tem só 0, 1 e −1: ela leva cada pixel da grade **exatamente** em outro pixel da grade, sem nenhuma posição fracionária. Não há reamostragem, não há pixel inventado nem perdido, e um sprite de 25 × 25 continua com 25 × 25. É por isso que o briefing estabelece, na seção 8.3, que as quatro direções das peças são geradas por rotação de 90°, que "não distorce pixel art".

## As peças da cobra

O gerador de sprites desenha cada peça em uma única orientação: a cabeça olhando para a direita, o corpo reto na horizontal, a curva ligando os lados esquerdo e de baixo, e a cauda presa à direita. As outras orientações são obtidas por rotação. O @cod:angulos mostra as tabelas que relacionam direções e ângulos.

::: codigo #angulos 270f2fc:src/cobrinha/ui/pecas.py 33-46
Ângulos de rotação por direção e o giro anti-horário dos lados
:::

Para escolher a peça e o ângulo de cada segmento, a função `classificar_pecas` (@cod:classificar) olha para os vizinhos de cada segmento. A cabeça aponta para longe do segmento seguinte; a cauda aponta para o anterior; um segmento do meio é reto se os vizinhos estão em lados opostos e é curva em caso contrário.

::: codigo #classificar 270f2fc:src/cobrinha/ui/pecas.py 93-113
Escolha da peça e da rotação de cada segmento (`classificar_pecas`)
:::

O caso mais elegante é o da curva. A curva-base liga os lados {esquerda, baixo}. Girada 90° no sentido anti-horário, cada lado vai para o seguinte da tabela `_GIRO_ANTI_HORARIO`: esquerda vira baixo e baixo vira direita, e a curva passa a ligar {baixo, direita}. A função `angulo_da_curva` (@cod:angulo-curva) gira o conjunto de lados da curva-base até ele coincidir com os lados pedidos e devolve o ângulo correspondente. Em vez de uma tabela com as quatro curvas escrita à mão, o código usa a própria definição da rotação.

::: codigo #angulo-curva 270f2fc:src/cobrinha/ui/pecas.py 83-90
Ângulo da curva obtido girando os lados da curva-base (`angulo_da_curva`)
:::

A @fig:rotacoes mostra a cabeça e a curva nas quatro rotações, produzidas pela própria chamada `pygame.transform.rotate` que o jogo usa.

::: figura rotacoes
Cabeça e curva giradas por `pygame.transform.rotate` em 0°, 90°, 180° e 270°
Fonte: elaborada pelos autores (2026).
largura: 72%
:::

## Pré-calcular as transformações

Rotacionar uma imagem tem custo, mesmo que pequeno. Como só existem 4 peças × 4 ângulos = 16 combinações, o jogo calcula todas uma única vez, ao criar a tela de jogo, e guarda o resultado num dicionário (@cod:sprites-init). Durante a partida, desenhar uma peça é só procurar a imagem pronta e fazer um `blit`. É a mesma troca de memória por tempo da pré-renderização do fundo (capítulo 6).

::: codigo #sprites-init 270f2fc:src/cobrinha/ui/pecas.py 116-124
As 16 rotações preparadas uma vez (`Sprites.__init__`)
:::

## Escala: vizinho mais próximo e interpolação

Ampliar uma imagem raster é reamostrá-la numa grade mais densa. Os dois métodos mais comuns são:

- **Vizinho mais próximo** (*nearest neighbor*): cada pixel novo copia a cor da amostra original mais próxima. Ampliando por um fator inteiro *k*, cada pixel vira um bloco de *k* × *k* pixels idênticos. As bordas continuam nítidas, e nenhuma cor nova é criada.
- **Interpolação bilinear**: cada pixel novo é uma média ponderada das quatro amostras vizinhas. O resultado é suave, adequado para fotos, mas borra contornos e cria cores intermediárias que não estavam na paleta.

A @fig:escala-vizinho-bilinear compara os dois métodos na maçã do jogo, ampliada 16 vezes.

::: figura escala-vizinho-bilinear
A maçã do jogo ampliada 16 vezes pelo vizinho mais próximo e por interpolação bilinear
Fonte: elaborada pelos autores (2026).
:::

Para pixel art, a escolha é o vizinho mais próximo. O projeto o usa em vários lugares: na redução das capturas do GIF de demonstração (`ferramentas/gravar_demo.py`, linha 116) e na geração do ícone do executável a partir da maçã (`ferramentas/empacotar.py`).

## Tela cheia sem borrar

O caso mais importante de escala no jogo é a janela. Com a opção `pygame.SCALED` (capítulo 3), o jogo desenha sempre em 800 × 600, e a SDL amplia a imagem para o tamanho da janela ou da tela. O filtro usado nessa ampliação é controlado pela dica `SDL_HINT_RENDER_SCALE_QUALITY`, que aceita `nearest` (vizinho mais próximo) ou `linear` (SDL, [20--]). No código-fonte do pygame-ce 2.5.8, ao criar o renderizador para o modo `SCALED`, a biblioteca define essa dica como `nearest` (arquivo `src_c/display.c`, linhas 1650 a 1655; Pygame-ce Developers, 2026). É por isso que a tela cheia do jogo não borra a pixel art, como prometia a seção 8.3 do briefing.

O mesmo trecho do código-fonte revela uma sutileza. Em modo janela, o pygame-ce pede à SDL uma escala **inteira** (`SDL_RenderSetIntegerScale`), e cada pixel lógico vira um bloco de 2 × 2, 3 × 3 etc. pixels físicos, todos do mesmo tamanho. Em tela cheia, o comentário do código explica que a escala inteira é desligada para usar a tela toda, "com pixels desiguais": numa tela de 1920 × 1080, por exemplo, o fator vertical seria 1080 / 600 = 1,8, e alguns pixels lógicos ocupariam 2 linhas físicas enquanto outros ocupariam só 1. A imagem continua nítida (não há mistura de cores), mas não perfeitamente regular. É uma troca entre aproveitar a tela e manter a grade perfeita, e a biblioteca escolheu aproveitar a tela.

<div class="caixa" markdown="1">
<p class="titulo-caixa">Experimente</p>

Num terminal Python, carregue um sprite com `pygame.image.load` e compare `pygame.transform.rotate(sprite, 90)` com `pygame.transform.rotate(sprite, 45)`. Imprima `get_size()` das duas superfícies e salve-as com `pygame.image.save` para ver o efeito da reamostragem no ângulo de 45°.
</div>
