# Cor: RGB, paleta e quantização

A cor de um pixel é, para o computador, um número. Para o olho humano, é uma sensação produzida pela luz. A CG precisa ligar os dois: escolher uma forma de codificar cores que seja eficiente para a máquina e que produza, na tela, as sensações desejadas. Este capítulo apresenta o modelo RGB, as paletas indexadas e a quantização de cores, e mostra como o jogo usa cada um.

## O modelo RGB

A retina humana tem três tipos de cones, sensíveis a faixas diferentes do espectro, e por isso três números bastam para descrever, de forma aproximada, a maioria das cores que enxergamos (Marschner; Shirley, 2021). Os monitores aproveitam esse fato: cada pixel é formado por três emissores, vermelho (*R*, de *red*), verde (*G*, de *green*) e azul (*B*, de *blue*), e a cor percebida é a soma das três luzes. É um modelo **aditivo**: (0, 0, 0) é o preto, a ausência de luz, e a soma das três no máximo é o branco.

Com 8 bits por canal, cada componente vai de 0 a 255, e são possíveis 256³ = 16 777 216 combinações. É essa a representação usada pelo pygame-ce, pela SDL e pelos arquivos PNG do jogo. No código, uma cor é uma tupla de três inteiros, como define o tipo `Cor` em `config.py`: `Cor = tuple[int, int, int]`.

Algumas relações do modelo ajudam a ler as cores do jogo. Quando os três canais são iguais, a cor é um cinza; quanto maiores, mais clara. A `Paleta` (@fig:paleta, no capítulo 7) não usa cinzas "puros": o `PRETO` é (20, 16, 26) e o `CINZA` é (98, 94, 110), ambos com um pouco mais de azul. Esse leve tom frio, comum em paletas de pixel art, faz as sombras parecerem menos "mortas" do que um cinza neutro.

## Paleta indexada

Guardar 24 bits por pixel nem sempre foi possível. Os primeiros *frame buffers* tinham 8 bits por pixel ou menos, e a saída foi a **cor indexada**: cada pixel guarda um índice, e uma tabela de cores, a **paleta** (*colormap*), traduz o índice para uma cor RGB completa (Heckbert, 1982). Com 8 bits por pixel, a imagem pode ter até 256 cores diferentes, mas cada uma delas pode ser qualquer uma das 16,7 milhões.

O pygame-ce ainda suporta esse formato: superfícies de 8 bits usam uma paleta para mapear seus valores para cores de 24 bits (Pygame-ce Developers, c2023). O jogo não usa superfícies indexadas, mas segue o espírito da técnica: todas as cores de sprites e interface vêm de uma única tabela de 16 entradas, a classe `Paleta` (@cod:paleta).

::: codigo #paleta 270f2fc:src/cobrinha/config.py 76-94
A paleta única do jogo (`config.py`)
:::

Uma paleta limitada traz três benefícios. Visualmente, ela dá unidade ao jogo, como discutido no capítulo 7. Tecnicamente, ela torna as imagens muito compressíveis: o PNG de cada sprite tem só algumas cores, e o GIF de demonstração pode ser guardado com poucas entradas de paleta sem perda visível. E, do ponto de vista do código, ela evita "números mágicos": nenhuma tela inventa uma cor nova; todas falam em `Paleta.VERMELHO`, `Paleta.AZUL_CLARO` etc.

## Quantização de cores

Às vezes é preciso fazer o caminho inverso: representar uma imagem com muitas cores usando poucas. Isso é a **quantização de cores**. O formato GIF, por exemplo, guarda cada quadro com uma paleta de no máximo 256 cores, e o GIF de demonstração do README é gravado a partir de capturas RGB do jogo.

A quantização mais simples é a **uniforme**: dividir cada canal em faixas fixas (por exemplo, 8 níveis de vermelho, 8 de verde e 4 de azul, totalizando 256 cores) e arredondar cada pixel para a faixa mais próxima. Ela ignora a imagem: reserva cores para regiões do espaço RGB que talvez nem apareçam e trata mal as que aparecem muito.

Heckbert (1982) propôs dividir o problema em quatro fases: (1) amostrar a imagem para obter estatísticas de cor; (2) escolher uma paleta com base nessas estatísticas; (3) mapear cada cor original para a cor mais próxima da paleta; (4) redesenhar a imagem, opcionalmente com pontilhado (*dithering*). Para a fase 2, ele apresentou o algoritmo de **corte pela mediana** (*median cut*):

1. Coloque todas as cores da imagem numa caixa, no espaço RGB.
2. Escolha a caixa a dividir e, nela, o eixo (R, G ou B) em que as cores estão mais espalhadas.
3. Divida a caixa na **mediana** das cores ao longo desse eixo, de modo que cada metade fique com o mesmo número de pixels.
4. Repita até ter tantas caixas quanto as cores desejadas; a cor representativa de cada caixa é a média das cores dentro dela.

Como cada corte divide a população de pixels ao meio, as regiões do espaço RGB com muitos pixels recebem muitas cores na paleta, e as regiões vazias não recebem nenhuma. Heckbert (1982) mostrou que, com isso, imagens que exigiriam 15 bits por pixel podiam ser reduzidas a 8 bits ou menos com pouca degradação perceptível, com resultado bem melhor que o da quantização uniforme.

## O median cut no GIF de demonstração

O script `ferramentas/gravar_demo.py` grava o GIF do README jogando o jogo sem janela. Na hora de salvar, cada quadro é quantizado pela biblioteca Pillow com o método de corte pela mediana, como mostra o @cod:quantizar.

::: codigo #quantizar ferramentas/gravar_demo.py 125-138
Quadros do GIF quantizados para 48 cores pelo corte pela mediana
:::

A documentação da Pillow informa que `Quantize.MEDIANCUT` é o método padrão para imagens RGB e que, se nada for dito, a quantização aplica pontilhado de Floyd-Steinberg (PILLOW..., [2026?]). O jogo pede 48 cores por quadro, bem abaixo do limite de 256 do GIF, e mesmo assim o resultado é praticamente indistinguível do original, porque cada quadro usa só as cores da paleta do jogo mais as misturas criadas pelas transparências (véus, fade e o antisserrilhamento das bordas, que no jogo é mínimo, porque os textos são desenhados sem suavização).

A @fig:quantizacao mostra um trecho de uma captura real quantizado para 48, 8 e 4 cores, sem pontilhado para deixar o efeito visível. Com 48 cores, não há diferença perceptível. Com 8, o algoritmo ainda preserva os dois verdes do xadrez e as cores principais. Com 4, as caixas do corte pela mediana precisam juntar cores muito diferentes, e detalhes como as rachaduras das pedras e as escamas da cobra desaparecem.

::: figura quantizacao
Trecho de uma captura do jogo quantizado pelo corte pela mediana para 48, 8 e 4 cores (sem pontilhado)
Fonte: elaborada pelos autores (2026), com a biblioteca Pillow.
largura: 72%
:::

## Cor e acessibilidade

Cor também é informação, e o briefing pede que ela não seja a única forma de transmiti-la (item I11). O jogo segue essa regra em vários pontos: o relógio do modo Contra o tempo fica vermelho abaixo de 10 s, mas continua mostrando os segundos em números; os power-ups ativos aparecem no HUD por escrito (`LENTO 4  X2 7`), e não só pelo véu azul; e a maçã dourada, além de amarela, vale mais pontos e mostra "+5" ao ser comida. A mesma lógica orienta a escolha das cores do HUD: texto claro sobre o cinza-escuro da faixa, com alto contraste.

<div class="caixa" markdown="1">
<p class="titulo-caixa">Experimente</p>

Abra uma captura do jogo com a Pillow e rode `imagem.quantize(colors=16, method=Image.Quantize.MEDIANCUT).getpalette()[:48]`. Compare as 16 cores escolhidas pelo algoritmo com as 16 cores da `Paleta`. Quais coincidem? Quais são misturas criadas pelas transparências?
</div>
