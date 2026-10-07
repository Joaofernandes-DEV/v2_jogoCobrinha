# Animação

Animar é mostrar uma sequência de imagens estáticas rápido o bastante para que o observador perceba movimento. Marschner e Shirley (2021) tratam a animação por computador como a especificação de como os parâmetros de uma cena variam ao longo do tempo; o computador calcula, para cada quadro, o valor de cada parâmetro e desenha a imagem correspondente. Lasseter (1987) mostrou que os princípios desenvolvidos pelos animadores tradicionais (temporização, aceleração e desaceleração, antecipação, exagero) continuam válidos quando as imagens são geradas por computador. Este capítulo apresenta as pequenas animações do Jogo da Cobrinha e termina com um estudo de caso: o movimento interpolado da cobra, que foi implementado e depois revertido.

## Animar em função do tempo

Há duas formas de escrever uma animação. Na primeira, cada quadro muda um pouco o parâmetro: "a cada quadro, suba 1 px". Na segunda, o parâmetro é uma **função do tempo**: "a posição é *f*(*t*)". A primeira depende da taxa de quadros: a 30 FPS, a animação fica duas vezes mais lenta do que a 60 FPS. A segunda não depende, e é a que o jogo usa em todas as animações.

Cada tela guarda um relógio próprio, somando o `dt` recebido em `atualizar` (por exemplo, `self.tempo += dt` em `EstadoJogando`), e as funções de desenho recebem esse tempo como parâmetro. É a mesma separação do capítulo 5, agora aplicada ao desenho: a lógica avança em passos fixos; as animações, em tempo contínuo.

## Flutuação senoidal

A maçã, a maçã dourada e os power-ups não ficam parados: sobem e descem levemente, chamando a atenção do jogador. O @cod:flutuar mostra como.

::: codigo #flutuar src/cobrinha/ui/pecas.py 173-178
Itens flutuando com um seno arredondado (`_desenhar_flutuando`)
:::

O deslocamento vertical é sen(4*t*), uma oscilação suave entre −1 e 1 com período de 2π/4 ≈ 1,57 s. O `round` da linha 177 é uma decisão de pixel art: em vez de posições fracionárias, que exigiriam reamostrar o sprite (capítulo 8), o item ocupa só três posições, −1, 0 e +1 px, e continua alinhado à grade de pixels. O resultado é um movimento "em degraus" que combina com o estilo do jogo, como mostra a parte (a) da @fig:grafico-animacoes.

::: figura grafico-animacoes
Funções de animação do jogo: (a) flutuação dos itens; (b) pisca-pisca dos itens que vão sumir; (c) opacidade dos textos flutuantes
Fonte: elaborada pelos autores (2026), com as constantes de `ui/pecas.py` e `ui/efeitos.py`.
:::

## Piscar

O pisca-pisca é a animação mais antiga dos jogos e uma forma eficiente de dizer "atenção". O jogo o usa em dois momentos.

Os itens temporários (maçã dourada e power-ups) piscam no último 1,5 s antes de sumir, para avisar o jogador de que o tempo está acabando (@cod:piscar).

::: codigo #piscar src/cobrinha/ui/pecas.py 151-163
Itens temporários piscando antes de sumir (`_desenhar_temporario`)
:::

A expressão `int(tempo * 8) % 2` vale 0 e 1 alternadamente, mudando a cada 1/8 s: o item aparece por 0,125 s e some por 0,125 s, quatro vezes por segundo, como mostra a parte (b) da @fig:grafico-animacoes. O item não é apagado: ele simplesmente deixa de ser desenhado naquele quadro.

O segundo uso é a animação de morte. Ao bater, a cobra pisca durante 0,9 s, com 7 alternâncias por segundo, antes da tela de fim de partida (`estados/jogando.py`, linhas 159 a 164). O intervalo dá ao jogador tempo de ver onde bateu, e as teclas são ignoradas nesse período, para que um toque nervoso não pule a tela de fim (diário de bordo, Fase 4). Terminada a animação, a tela de fim de partida é empilhada sobre o campo congelado (@fig:captura-fim).

::: figura captura-fim
Tela de fim de partida, empilhada sobre o campo congelado depois da animação de morte
Fonte: captura de tela do jogo, elaborada pelos autores (2026).
largura: 65%
:::

Piscar pode incomodar algumas pessoas e, em casos extremos, é um risco para pessoas com fotossensibilidade. Por isso a tela de opções tem "efeitos visuais: NÃO", que desliga o pisca-pisca da morte e os textos flutuantes (item I11 do briefing).

## Textos que sobem e somem

Ao comer, um texto como "+1" sobe 30 px e desaparece em 0,8 s (@cod:texto-flutuante, no capítulo 10). Com *p* = idade / 0,8 indo de 0 a 1, a altura cresce linearmente, 30*p*, mas a opacidade segue 255 × (1 − *p*²), parte (c) da @fig:grafico-animacoes. A curva quadrática faz o texto ficar quase opaco no início e sumir rapidamente no fim. Na linguagem de Lasseter (1987), é uma forma de *slow in*: a mudança começa devagar e acelera, de modo que o jogador tem tempo de ler o valor antes de ele desaparecer.

## Estudo de caso: o movimento interpolado

A decisão D1 do briefing estabeleceu que a cobra se moveria célula a célula, "fiel ao clássico e à pixel art", e deixou o movimento suave para a V3. O primeiro trabalho da V3, em 2 de outubro de 2026, às 22:44, foi exatamente esse (*pull request* 2). Às 23:07, João Vitor decidiu desfazê-lo (*pull request* 4). O episódio, bem documentado no diário de bordo e no histórico do Git, é um bom exemplo de decisão de projeto em CG.

### A técnica

Fiedler (2004) propõe, ao final da sua discussão sobre passo fixo, que o desenho seja feito **entre** os dois últimos estados da simulação, usando a fração do passo que já se passou. Na V3, essa fração foi exposta pela propriedade `progresso_passo` da partida: o valor do acumulador dividido pelo intervalo do passo (@cod:progresso-passo).

::: codigo #progresso-passo c0fa005^:src/cobrinha/dominio/partida.py 118-126
Fração do passo atual, usada para interpolar o desenho (versão removida)
:::

A cobra passou a lembrar, para cada segmento, de onde ele saiu no último passo e onde está agora (`Cobra.trajetos`, no commit `ba941b8`), e a interface calculava a posição intermediária por **interpolação linear** entre as duas células (@cod:interpolar-celula).

::: codigo #interpolar-celula 890ad71:src/cobrinha/ui/campo.py 22-36
Interpolação linear entre duas células vizinhas (versão removida)
:::

A interpolação linear entre dois pontos *P*<sub>0</sub> e *P*<sub>1</sub>, *P*(*t*) = *P*<sub>0</sub> + *t* (*P*<sub>1</sub> − *P*<sub>0</sub>), com *t* entre 0 e 1, é a forma mais simples de produzir quadros intermediários a partir de quadros-chave (Marschner; Shirley, 2021). As linhas 30 a 33 tratam o caso do modo Sem bordas: quando a cabeça sai por um lado e entra pelo outro, as células de origem e destino estão a 31 colunas de distância, e a interpolação ingênua faria o segmento atravessar o campo inteiro em um passo. O código detecta o salto e o converte em um deslocamento de uma célula "para fora", e o `%` das linhas 34 e 35 traz o resultado de volta ao campo. O capítulo 12 mostra como esse segmento era desenhado dos dois lados da borda.

### O custo: um passo de atraso

O diário de bordo registra a consequência principal já na entrada que introduz a técnica: "o desenho fica até um passo atrás da lógica". A @fig:grafico-interpolacao mostra o porquê. Na lógica (curva vermelha), a cabeça muda de célula instantaneamente no início de cada passo. No desenho interpolado (curva azul), ela sai da célula anterior e só chega à célula atual no fim do passo. Quando a lógica já decidiu que a cobra comeu a maçã, a cabeça desenhada ainda está a caminho, e a maçã some antes de a cabeça chegar até ela.

::: figura grafico-interpolacao
Posição da cabeça na lógica (degraus) e no desenho interpolado (rampas): o desenho fica até uma célula atrás
Fonte: elaborada pelos autores (2026), a 8 passos por segundo.
:::

A 8 passos por segundo, esse atraso chega a 125 ms. Num jogo em que o jogador reage ao que vê, a diferença entre o que está na tela e o que vale para as regras não é só estética: a cobra pode bater num obstáculo que, na tela, ainda parece estar a meia célula de distância.

### O que o diário de bordo registra

Os registros de 2 de outubro de 2026 permitem montar o quadro de prós e contras do @qua:interpolacao.

::: quadro #interpolacao
Prós e contras do movimento interpolado, segundo o diário de bordo
Fonte: elaborado pelos autores (2026) com base no `LOG.md` (entradas de 2 de outubro de 2026, 22:44 e 23:07).
| A favor | Contra |
|---|---|
| Movimento contínuo, sem "pulos" de célula em célula | O desenho fica até um passo atrás da lógica: a comida some antes de a cabeça chegar |
| Regras e testes do domínio inalterados: colisão, comida e pontos continuam no passo discreto | Os sprites continuam presos à grade: a orientação da cabeça e das curvas muda de uma vez, por célula, e só a posição é suavizada |
| A técnica é padrão na literatura (Fiedler, 2004) | Mais código: trajetos, fração do passo, interpolação, desenho dos dois lados da borda com recorte e 9 testes a mais |
| — | Afasta-se do estilo escolhido: o clássico e a pixel art são discretos (decisão D1) |
:::

A decisão final, registrada às 23:07, foi de design: João Vitor testou o movimento suave e preferiu o discreto, "fiel ao clássico e à pixel art". A remoção foi feita depois do merge dos *pull requests* 1 a 3, "para o histórico registrar a tentativa e a volta", e o número de testes voltou de 222 para 213.

### Lições do caso

O caso ilustra três pontos gerais. Primeiro, a separação entre modelo e visão (capítulo 12) permitiu experimentar uma técnica de desenho sem tocar nas regras: a interpolação morava inteira na interface, e a lógica só expôs dois dados novos. Segundo, uma técnica correta e bem documentada na literatura pode não ser a certa para um jogo específico: interpolar é ótimo para simulações físicas a 60 Hz, mas a 8 passos por segundo o atraso fica perceptível. Terceiro, registrar decisões revertidas tem valor: sem o diário de bordo e os *pull requests*, esse aprendizado teria se perdido.

<div class="caixa" markdown="1">
<p class="titulo-caixa">Experimente</p>

Recupere a versão interpolada com `git switch --detach ddb474b` (o merge do *pull request* 2) e jogue no nível 3, o mais rápido. Repare na maçã sumindo antes de a cabeça chegar e na troca brusca de orientação da cabeça nas curvas. Volte com `git switch -`.
</div>
