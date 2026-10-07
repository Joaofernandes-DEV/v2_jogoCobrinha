# Transparência e composição alfa

Uma maçã de 25 × 25 pixels não é um quadrado: é um círculo com cabinho e folha, e os pixels em volta dela devem deixar ver a grama. Uma tela de pausa não apaga a partida: escurece o campo e deixa o jogador ver onde a cobra parou. Esses dois efeitos dependem do mesmo conceito, a **transparência**, e da operação que combina uma imagem sobre outra, a **composição** (*compositing*). Este capítulo apresenta o canal alfa e o operador *over* de Porter e Duff (1984) e mostra os quatro usos de transparência no jogo.

## O canal alfa

Porter e Duff (1984) defenderam que imagens geradas por computador deveriam ter **quatro canais**: os três de cor e um quarto, que chamaram de *matte* e que hoje conhecemos como **canal alfa** (o "A" de RGBA). O alfa de um pixel diz quanto daquele pixel é coberto pela imagem: 1 (ou 255, com 8 bits) significa totalmente opaco; 0 significa totalmente transparente; valores intermediários indicam cobertura parcial, como nas bordas suavizadas de uma forma ou numa camada semitransparente. Os autores mostraram que esse canal pode ser calculado e armazenado junto com as cores e, a partir dele, definiram uma **álgebra de composição**: um conjunto de operadores para combinar duas imagens.

Sem alfa, uma imagem retangular só pode substituir o que está embaixo. Era o problema da maçã da V1, registrado no briefing: o arquivo `comida.jpg` não tinha transparência, porque o formato JPEG não guarda canal alfa, e um quadrado de fundo aparecia em volta da fruta. Na V2, todos os sprites são PNGs com alfa, criados sobre uma superfície totalmente transparente (`pygame.SRCALPHA`, com todos os pixels em (0, 0, 0, 0)), como faz a função `nova_superficie` do gerador de sprites (`ferramentas/gerar_sprites.py`, linhas 57 a 60).

## O operador *over*

Dos operadores de Porter e Duff (1984), o mais usado é o *over*: a imagem *A* sobre a imagem *B*. Para um fundo *B* opaco e uma cor *A* com alfa *α* entre 0 e 1, a cor resultante *C*, canal a canal, é:

<p class="formula">C = α · A + (1 − α) · B</p>

Ou seja, uma média ponderada: *α* da cor de cima e o restante da cor de baixo. Com *α* = 1, só *A* aparece; com *α* = 0, só *B*. Porter e Duff trabalham com cores **pré-multiplicadas** pelo alfa (guardando *α* · *A* em vez de *A*), o que simplifica a álgebra quando as duas imagens têm transparência. Para o caso do jogo, com fundo sempre opaco, a fórmula acima basta.

## Exemplo numérico: o véu azul da câmera lenta

Quando o power-up de câmera lenta está ativo, a tela de jogo pinta sobre o campo uma camada azul com alfa 40 (em 255), criada uma vez no início da partida (`estados/jogando.py`, linhas 86 e 87). Tomemos um pixel da grama clara, de cor (142, 196, 78), sob o azul (64, 112, 178), com *α* = 40/255 ≈ 0,157:

<p class="formula">R = 0,157 · 64 + 0,843 · 142 ≈ 130</p>
<p class="formula">G = 0,157 · 112 + 0,843 · 196 ≈ 183</p>
<p class="formula">B = 0,157 · 178 + 0,843 · 78 ≈ 94</p>

A captura da @fig:captura-camera-lenta, gerada rodando o jogo, tem exatamente a cor (130, 183, 94) nesse pixel, enquanto a captura do mesmo instante sem o power-up (@fig:captura-jogando, no capítulo 3) tem (142, 196, 78). O azul é sutil de propósito: ele avisa o jogador sem atrapalhar a leitura do campo, e o efeito também é escrito no HUD ("LENTO 5"), como discutido no capítulo 9.

::: figura captura-camera-lenta
Câmera lenta e pontos em dobro ativos: o véu azul sobre o campo e os efeitos escritos no HUD
Fonte: captura de tela do jogo, elaborada pelos autores (2026).
largura: 72%
:::

A composição também pode ser **encadeada**. Na captura da pausa (@fig:captura-pausa, no capítulo 6), feita com a câmera lenta ainda ativa, o mesmo pixel recebe primeiro o véu azul e depois o véu preto da pausa, (20, 16, 26) com alfa 170. Aplicando o *over* outra vez sobre (130, 183, 94), com *α* = 170/255 ≈ 0,667, obtém-se aproximadamente (57, 72, 49); a captura tem (57, 72, 48), diferença de uma unidade explicada pelos arredondamentos da SDL. A ordem importa: o *over* não é comutativo, e é o algoritmo do pintor (capítulo 6) que garante a ordem certa.

## Alfa por pixel e alfa da superfície

O pygame-ce oferece dois tipos de transparência (Pygame-ce Developers, c2023):

- **Alfa por pixel**: cada pixel tem seu próprio alfa. Surge em superfícies criadas com `pygame.SRCALPHA` ou convertidas com `convert_alpha()`. É o que recorta a maçã em forma de círculo.
- **Alfa da superfície**: um único valor, definido com `set_alpha`, que vale para a superfície inteira. A documentação registra que, desde o pygame 2.0, ele pode ser combinado com o alfa por pixel.

O jogo usa os dois, e a @fig:composicao-alfa mostra o mesmo trecho do campo sob três das camadas reais.

::: figura composicao-alfa
O mesmo trecho do campo sem camada, sob o véu azul (α = 40), sob o véu da pausa (α = 170) e sob o fade no meio da transição (α = 128)
Fonte: elaborada pelos autores (2026), usando as funções e constantes do jogo.
:::

### Véus escuros das telas empilhadas

As telas que ficam por cima da partida (pausa, contagem, nível concluído, fim de partida) e as telas de menu usam um véu criado pela função do @cod:veu: uma superfície do tamanho da janela, com alfa por pixel, preenchida com o preto da paleta e a opacidade pedida.

::: codigo #veu src/cobrinha/ui/painel.py 14-18
Véu escuro semitransparente (`criar_veu`)
:::

Cada tela escolhe sua opacidade: 150 na contagem e no menu, 170 na pausa e no fim de partida, 200 nas telas de recordes, opções e créditos, em que o texto é longo e o fundo precisa atrapalhar menos. O diário de bordo registra um ajuste feito a partir das capturas: o véu da contagem ficou mais escuro porque as pedras do nível 2 apareciam atrás do nome do nível.

### O fade de transição

Ao trocar de tela, o jogo faz a nova tela "surgir do preto" em 0,25 s. A técnica é a mais simples possível: uma superfície preta do tamanho da janela, sem alfa por pixel, desenhada por cima de tudo com alfa de superfície decrescente. No método `Jogo._desenhar` (@cod:desenhar, no capítulo 3), as linhas 124 e 125 fazem `set_alpha(round(255 * opacidade_fade))` e o `blit`, e o laço principal reduz `opacidade_fade` de 1 a 0 ao longo da transição. Pelo *over*, cada pixel da tela vai do preto à sua cor real por interpolação linear.

### Textos que somem

Os textos flutuantes ("+1", "X2!") sobem e desaparecem em 0,8 s. O @cod:texto-flutuante mostra que o desaparecimento é um alfa de superfície que cai de 255 a 0.

::: codigo #texto-flutuante src/cobrinha/ui/efeitos.py 37-43
Texto flutuante com alfa decrescente (`Efeitos.desenhar`)
:::

Há um detalhe importante na linha 40: o `.copy()`. A função `texto.renderizar` guarda as imagens de texto em cache (capítulo 13), e a mesma superfície do "+1" amarelo é reaproveitada por todos os textos iguais. Se o código mudasse o alfa da superfície em cache, todos os "+1" da tela, inclusive os recém-criados, ficariam com a mesma transparência. A cópia isola o efeito. A curva do alfa, 255 × (1 − *p*²), é discutida no capítulo 11.

<div class="caixa" markdown="1">
<p class="titulo-caixa">Para ir além</p>

Porter e Duff (1984) definem doze operadores de composição, entre eles *over*, *in*, *out*, *atop* e *xor*. O pygame-ce oferece modos de mistura por meio do parâmetro `special_flags` do `blit` (por exemplo, `pygame.BLEND_RGBA_MULT`). Como você usaria um desses modos para escurecer o campo sem criar uma superfície de véu?
</div>
