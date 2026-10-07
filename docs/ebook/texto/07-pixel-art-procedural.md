# Pixel art gerada por código

A V1 usava sprites desenhados em outras ferramentas, com até 840 × 462 px, que o jogo esticava para 30 × 30 px a cada quadro. O resultado eram imagens distorcidas e borradas (briefing, seção 2.3). A V2 inverteu a lógica: os sprites passaram a ser desenhados **no tamanho exato de uso**, 25 × 25 px, pixel a pixel, por um programa: `ferramentas/gerar_sprites.py`. Este capítulo mostra como formas geométricas descritas por funções viram pixel art, e por que gerar arte por código é uma escolha interessante num projeto de CG.

## Pixel art e paleta limitada

*Pixel art* é o estilo em que cada pixel é posicionado deliberadamente e permanece visível como um bloco de cor. Ele nasceu da limitação dos primeiros computadores e consoles, com resolução baixa e poucas cores simultâneas, e hoje é usado como escolha estética. Duas regras do estilo orientam o projeto: os sprites são desenhados na resolução final, sem redimensionamento, e usam uma **paleta limitada**.

A paleta do jogo tem 16 cores, definidas na classe `Paleta` do `config.py` e usadas tanto pelos sprites quanto pela interface (HUD, menus e textos). A @fig:paleta mostra as 16 cores com seus valores RGB. Ter uma paleta única dá coesão visual ao jogo: a sombra da maçã, a terra do cabinho e o chapéu do cogumelo usam o mesmo marrom, e o verde-escuro do contorno da cobra é o mesmo das escamas. O capítulo 9 volta a esse assunto do ponto de vista da teoria das cores.

::: figura paleta
A paleta de 16 cores do jogo (classe `Paleta`, em `config.py`), com os valores RGB
Fonte: elaborada pelo autor (2026) com `docs/ebook/figuras.py`, a partir de `src/cobrinha/config.py`.
largura: 80%
:::

A @fig:sprites-ampliados mostra todos os sprites gerados, ampliados oito vezes com o método do vizinho mais próximo (capítulo 8), para que cada pixel possa ser visto. O xadrez cinza ao fundo indica as áreas transparentes.

::: figura sprites-ampliados
Os dez sprites do jogo (25 × 25 px), ampliados 8 vezes pelo vizinho mais próximo
Fonte: elaborada pelo autor (2026) a partir dos PNGs gerados por `ferramentas/gerar_sprites.py`.
:::

## Formas descritas por funções

Como dizer a um programa "desenhe uma maçã"? A resposta do gerador é descrever cada forma por uma **função de pertinência**: uma função `dentro(x, y)` que responde se o pixel (*x*, *y*) faz parte da forma. Para pintar a forma, basta percorrer os 625 pixels da célula e colorir aqueles para os quais a função responde que sim.

Esse é o princípio das **curvas implícitas**, apresentadas por Marschner e Shirley (2021): uma curva definida por uma equação *f*(*x*, *y*) = 0, que divide o plano em pontos com *f* < 0 (dentro) e *f* > 0 (fora). Um círculo de raio *r* e centro (*c*<sub>x</sub>, *c*<sub>y</sub>) é o conjunto dos pontos em que a distância ao centro é igual a *r*; seu interior, os pontos em que essa distância é menor. O @cod:maca mostra exatamente isso no desenho da maçã.

::: codigo #maca ferramentas/gerar_sprites.py 163-177
Corpo e sombra da maçã por uma função de distância (`comida`)
:::

Dois detalhes do código são conceitos de CG.

O primeiro é o `+ 0.5` nas linhas 169 e 175. O pixel (*x*, *y*) é tratado como uma **amostra no seu centro**, (*x* + 0,5, *y* + 0,5), e não no canto superior esquerdo. É a mesma visão de Smith (1995), para quem um pixel é uma amostra pontual. Sem esse deslocamento, as formas sairiam meio pixel deslocadas para cima e para a esquerda e perderiam a simetria.

O segundo é a sombra da linha 175. A condição (*x* − *c*<sub>x</sub>) + (*y* − *c*<sub>y</sub>) > 0,9 *r* descreve um **semiplano**: todos os pontos de um lado de uma reta diagonal. Os pixels da maçã que caem nesse semiplano, no canto inferior direito, recebem a cor de sombra. O resultado sugere uma luz vindo do canto superior esquerdo, convenção comum na pixel art e seguida em todos os sprites do jogo (veja a pedra e o cogumelo na @fig:sprites-ampliados).

## O anel da curva

A peça mais interessante é a curva do corpo da cobra, que liga dois lados vizinhos da célula. O @cod:curva desenha um **quarto de anel**: os pixels cuja distância ao canto inferior esquerdo da célula fica entre 4 e 21 px.

::: codigo #curva ferramentas/gerar_sprites.py 90-104
A curva do corpo como um quarto de anel (`corpo_curva`)
:::

A distância *d* ao centro, menos a borda de 4 px, vira a **profundidade** do pixel dentro do corpo: 0 na borda interna e 16 na externa. A @fig:curva-distancia mostra o sprite ampliado com os dois círculos que delimitam o anel.

::: figura curva-distancia
Sprite da curva ampliado 24 vezes, com os círculos de raio 4 (vermelho) e 21 (azul) centrados no canto inferior esquerdo
Fonte: elaborada pelo autor (2026) com `docs/ebook/figuras.py`, a partir de `corpo_curva.png`.
largura: 72%
:::

O ganho dessa formulação é que o corpo reto e a curva usam **a mesma função de cor**. No corpo reto, a profundidade de um pixel é a distância vertical até a borda superior do corpo (`y - BORDA_CORPO`, linha 86); na curva, é a distância radial. Como a cor depende só da profundidade, as duas peças se encaixam sem emenda: a faixa clara do meio do corpo reto continua exatamente na faixa clara da curva.

## Sombreamento por faixas

A função `cor_do_corpo`, no @cod:cor-do-corpo, transforma a profundidade em cor. É um sombreamento em faixas: contorno preto nas bordas, verde-escuro logo dentro, verde no corpo e verde-claro no centro, que dá a impressão de um corpo cilíndrico iluminado de frente.

::: codigo #cor-do-corpo ferramentas/gerar_sprites.py 38-54
Cor de um pixel do corpo em função da profundidade (`cor_do_corpo`)
:::

As escamas em "V" do corpo reto (linha 49) usam a posição ao longo do corpo: um pixel é escama quando a soma da posição com a distância ao meio é múltipla de 8, o que desenha diagonais que se encontram no centro. Na curva, o parâmetro `ao_longo` é `None` e não há escamas. O diário de bordo explica por quê: dobradas no arco, as escamas ficavam distorcidas, e a decisão foi tirada das capturas de tela da Fase 3.

## Contorno por vizinhança

O contorno preto das formas é calculado, e não desenhado à mão. A função `contornar`, no @cod:contorno, pinta de preto todo pixel da forma que tem pelo menos um **vizinho de 4** (esquerda, direita, acima ou abaixo) fora da forma.

::: codigo #contorno ferramentas/gerar_sprites.py 63-79
Contorno calculado pela vizinhança de 4 (`contornar`)
:::

O parâmetro `abertos` resolve um problema de encaixe: a cabeça, a cauda e o corpo continuam na célula vizinha, e por isso não podem ter contorno no lado por onde se ligam. A cabeça, por exemplo, é contornada com `abertos={"esq"}`, porque o pescoço sai pela esquerda.

A escolha da vizinhança de 4, e não de 8 (que incluiria as diagonais), produz um contorno de 1 pixel que nunca fica "grosso" nas diagonais, o que é desejável na pixel art.

## Por que gerar arte por código

O briefing e o diário de bordo registram as vantagens que motivaram essa escolha:

- **Reprodutibilidade**: o gerador é determinístico. Rodar `python ferramentas/gerar_sprites.py` recria exatamente os mesmos PNGs, e o diário de bordo registra que, ao acrescentar os power-ups na V3, os sprites antigos foram regenerados e saíram idênticos.
- **Coesão**: todos os sprites usam a mesma paleta e as mesmas convenções de luz, contorno e espessura.
- **Ajuste fino**: mudar a espessura do corpo (`ESPESSURA = 17`) ou a cor da sombra recalcula todas as peças de uma vez, mantendo o encaixe.
- **Testabilidade**: `tests/test_recursos.py` confere o tamanho de 25 × 25 px e a transparência dos sprites gerados.
- **Documentação**: o script é, ele próprio, a descrição de como cada asset foi feito. As regras do repositório (`CLAUDE.md` e `CONTRIBUTING.md`) proíbem editar os PNGs à mão: muda-se o gerador e regenera-se.

<div class="caixa" markdown="1">
<p class="titulo-caixa">Experimente</p>

Mude `ESPESSURA = 17` para `13` em `ferramentas/gerar_sprites.py`, regenere os sprites e jogue uma partida. Observe que a curva e o corpo reto continuam se encaixando. Depois, desfaça a mudança com `git checkout -- src/cobrinha/assets ferramentas/gerar_sprites.py`.
</div>
