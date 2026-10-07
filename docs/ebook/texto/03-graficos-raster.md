# Gráficos raster: pixel, resolução e framebuffer

Quase toda tela moderna é um dispositivo **raster**: a imagem é uma matriz retangular de pontos, e cada ponto recebe uma cor. Marschner e Shirley (2021) observam que, mesmo quando a cena é descrita por formas contínuas (retas, círculos, polígonos), ela precisa ser convertida em uma imagem raster para ser exibida. Este capítulo apresenta os conceitos básicos desse modelo (pixel, resolução, framebuffer e buffer duplo) e mostra como o pygame-ce os expõe.

## Imagens vetoriais e imagens raster

Uma imagem **vetorial** descreve formas: "um círculo de raio 8 centrado em (12,5; 14,5)". Uma imagem **raster** descreve amostras: "o pixel (12, 14) é vermelho". A primeira pode ser ampliada sem perda, porque basta recalcular a forma; a segunda tem uma resolução fixa. O Sketchpad, citado no capítulo 1, desenhava vetores diretamente na tela (Sutherland, 1963); os monitores atuais e a biblioteca pygame-ce trabalham com rasters.

O Jogo da Cobrinha mostra as duas ideias convivendo. Os sprites são gerados a partir de descrições geométricas (o corpo da maçã é "todo pixel cuja distância ao centro é menor que 8,5"), mas o que se grava no arquivo PNG e o que se desenha na tela é sempre uma matriz de pixels (capítulo 7).

## O que é um pixel

O termo *pixel* vem de *picture element*. É comum imaginá-lo como um pequeno quadrado colorido, mas Smith (1995) argumenta que essa imagem é enganosa: um pixel é uma **amostra pontual** de uma imagem contínua, e o "quadradinho" que vemos é só o resultado de como o monitor reconstrói essa amostra. A distinção importa quando se amplia ou se gira uma imagem: para decidir a cor de um novo pixel, é preciso decidir como reconstruir a imagem entre as amostras (capítulo 8).

No caso da pixel art, porém, a convenção do "quadradinho" é exatamente o efeito desejado: cada pixel do sprite deve aparecer como um bloco nítido de cor uniforme. É por isso que o projeto toma cuidado para nunca suavizar os sprites, como se verá nos capítulos 7 e 8.

## Resolução e memória

A **resolução** de uma imagem raster é o número de colunas e linhas de pixels. A janela do jogo tem 800 × 600 = 480 000 pixels. Se cada pixel ocupar 4 bytes (vermelho, verde, azul e alfa, com 8 bits cada), um quadro inteiro ocupa 1 920 000 bytes, cerca de 1,9 MB. Esse cálculo simples explica um problema histórico da área: até o fim da década de 1970, memória para guardar uma imagem inteira era cara, e por isso os primeiros *frame buffers* usavam poucos bits por pixel e uma tabela de cores (Heckbert, 1982), assunto do capítulo 9.

A @fig:captura-jogando é um quadro real do jogo, exatamente como ele fica na memória antes de ser mostrado: 800 × 600 pixels, com a faixa do HUD no topo e o campo de 32 × 22 células abaixo.

::: figura captura-jogando
Um quadro do jogo (nível 2): HUD, pedras, maçã, maçã dourada, power-up de câmera lenta e o texto "+1" logo depois de comer
Fonte: captura de tela do jogo, elaborada pelos autores (2026).
largura: 72%
:::

## Superfícies no pygame-ce

No pygame-ce, toda imagem raster é uma `pygame.Surface`: uma matriz de pixels com resolução e formato de pixel fixos (Pygame-ce Developers, c2023). A janela também é uma superfície, devolvida por `pygame.display.set_mode`. Desenhar, no pygame-ce, significa alterar os pixels de uma superfície: preencher um retângulo (`fill`), mudar um pixel (`set_at`) ou copiar outra superfície para dentro dela (`blit`).

O **formato de pixel** é a forma como cada cor é codificada na memória (quantos bits por canal, em que ordem, e se há canal alfa). Copiar uma superfície para outra de formato diferente obriga a biblioteca a converter cada pixel no caminho. Por isso a documentação recomenda converter as imagens carregadas para o formato da tela: `convert()` para imagens opacas e `convert_alpha()` para imagens com transparência por pixel (Pygame-ce Developers, c2023). O @cod:imagem mostra como o jogo faz isso uma única vez por sprite, guardando o resultado em cache.

::: codigo #imagem src/cobrinha/recursos.py 36-39
Carregamento único de um sprite, convertido para o formato da tela
:::

O decorador `@cache` garante que cada PNG seja lido do disco e convertido uma só vez (item D6 do briefing). O comentário da função lembra uma restrição importante: a conversão precisa de uma janela aberta, porque o formato de destino é o da tela.

## Framebuffer e buffer duplo

O **framebuffer** é a região de memória que guarda a imagem a ser exibida. Se o programa desenhasse diretamente na imagem que o monitor está lendo, o usuário poderia ver o quadro pela metade: o fundo já pintado, mas a cobra ainda não. O efeito, conhecido como *tearing* ou cintilação, é evitado com o **buffer duplo**: o programa desenha num buffer de trás (*back buffer*), invisível, e só quando o quadro está completo os papéis se invertem e ele passa a ser exibido. Nystrom (2014) descreve essa técnica como o padrão *Double Buffer*, cuja ideia central é fazer uma sequência de operações parecer instantânea para quem observa.

No pygame-ce, essa troca é feita por `pygame.display.flip()`, que atualiza a tela inteira com o conteúdo da superfície da janela; no modo OpenGL, ela faz a troca de buffers (Pygame-ce Developers, c2023). O @cod:desenhar mostra o método do jogo que monta cada quadro e termina com o `flip()`.

::: codigo #desenhar src/cobrinha/jogo.py 119-126
Montagem de um quadro em `Jogo._desenhar()`, encerrada pelo `flip()`
:::

Entre o `fill` da linha 120 e o `flip` da linha 126, nada do que é desenhado aparece para o jogador. Só o quadro completo (fundo, HUD, cobra, telas empilhadas e o fade) é mostrado, de uma vez. O capítulo 6 detalha a ordem dessas etapas.

<div class="caixa" markdown="1">
<p class="titulo-caixa">Para ir além</p>

A janela é criada com a opção `pygame.SCALED` (`src/cobrinha/jogo.py`, linha 46). Nesse modo, o código-fonte do pygame-ce 2.5.8 cria um renderizador da SDL associado à janela e define a resolução lógica com `SDL_RenderSetLogicalSize` (arquivo `src_c/display.c`, linhas 1648 a 1705; Pygame-ce Developers, 2026). O jogo continua desenhando numa superfície de 800 × 600, e a SDL apresenta essa imagem ampliada na janela real. O capítulo 8 mostra por que essa ampliação não borra a pixel art.
</div>
