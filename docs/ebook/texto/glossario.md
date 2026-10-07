# Glossário

Acumulador
:   Variável que guarda o tempo real ainda não consumido pela simulação, no passo de tempo fixo. A cada quadro recebe o `dt` e, a cada passo executado, perde um intervalo.

Algoritmo do pintor
:   Método de visibilidade em que os objetos são desenhados do mais distante para o mais próximo, cada um cobrindo os anteriores.

Alfa (canal)
:   Quarto canal de uma imagem RGBA, que indica a opacidade (cobertura) de cada pixel: 0 é transparente e o valor máximo é opaco.

Amostragem
:   Representação de um sinal contínuo (imagem ou som) por valores medidos em pontos ou instantes regulares.

Blit
:   Cópia de um bloco retangular de pixels de uma superfície para outra (*bit block transfer*), combinando as cores quando há transparência.

Buffer duplo
:   Técnica em que o quadro é desenhado num buffer invisível e só exibido quando está completo, evitando que o usuário veja o desenho pela metade.

Coordenadas homogêneas
:   Representação de um ponto do plano (*x*, *y*) como (*x*, *y*, 1), que permite escrever translações, rotações e escalas como multiplicações de matrizes 3 × 3.

Corte pela mediana (*median cut*)
:   Algoritmo de quantização de cores que divide recursivamente o conjunto de cores da imagem na mediana do eixo de maior variação, de modo que cada cor da paleta represente uma parte igual dos pixels.

Envelope
:   Variação do volume de um som ao longo do tempo (ataque, sustentação, soltura), que evita estalos e dá forma ao timbre.

Envolvimento de bordas
:   Regra em que um objeto que sai por uma borda do campo reaparece na borda oposta, como na superfície de um toro.

Fade
:   Transição em que a imagem surge do preto (ou desaparece no preto) pela variação gradual da opacidade de uma camada.

Framebuffer
:   Região de memória que guarda a cor de cada pixel da imagem a ser exibida.

Glifo
:   Desenho de um caractere numa fonte específica.

HUD
:   Faixa de informações sobreposta ou adjacente à área de jogo (pontos, nível, tempo).

Interpolação linear
:   Cálculo de um valor intermediário entre dois valores conhecidos, proporcional a um parâmetro entre 0 e 1.

Laço de jogo
:   Laço principal que, a cada volta, processa a entrada, atualiza o estado e desenha o quadro, controlando a passagem do tempo.

Paleta
:   Conjunto limitado de cores usado por uma imagem ou por um jogo; na cor indexada, tabela que traduz índices em cores RGB.

Passo de tempo fixo
:   Técnica em que a simulação avança em intervalos de duração constante, independentes da taxa de quadros do desenho.

Pixel
:   Menor elemento de uma imagem raster; uma amostra de cor numa posição da grade.

Pixel art
:   Estilo gráfico em que cada pixel é posicionado deliberadamente e permanece visível como bloco de cor.

Quantização de cores
:   Redução do número de cores de uma imagem, escolhendo uma paleta e mapeando cada cor original para a mais próxima dela.

Raster
:   Representação de uma imagem como matriz retangular de pixels.

Recorte (*clipping*)
:   Eliminação das partes de uma primitiva ou imagem que ficam fora de uma região, normalmente a área visível.

Sprite
:   Imagem pequena, normalmente com transparência, desenhada sobre o fundo para representar um objeto do jogo.

Superfície (`pygame.Surface`)
:   Objeto do pygame-ce que representa uma imagem raster com resolução e formato de pixel fixos.

Taxa de quadros
:   Número de imagens desenhadas por segundo (FPS).

Transformação afim
:   Transformação geométrica que combina uma transformação linear (rotação, escala) com uma translação.

Vizinho mais próximo
:   Método de reamostragem em que cada pixel novo copia a cor da amostra original mais próxima, sem criar cores intermediárias.
