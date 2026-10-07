# Introdução

Todo jogo de computador é, antes de qualquer coisa, um programa que desenha. Sessenta vezes por segundo ele decide a cor de cada um dos milhares de pixels da janela, e é dessa sequência de imagens que o jogador tira a ilusão de movimento, de profundidade e de um mundo que reage aos seus comandos. Estudar como essas imagens são produzidas é o objeto da Computação Gráfica (CG).

Este ebook usa um projeto real, o Jogo da Cobrinha desenvolvido para a disciplina de Computação Gráfica da Universidade Paulista (UNIP), como fio condutor para apresentar os conceitos fundamentais da área. Cada capítulo explica um conceito com base na literatura e mostra, em seguida, onde e como ele aparece no código do jogo, com trechos copiados diretamente do repositório e identificados por arquivo e número de linha.

## Objetivo e público

O objetivo é que o leitor consiga, ao final, ligar a teoria clássica de CG (raster, sistemas de coordenadas, transformações, cor, composição alfa, animação e recorte) a decisões concretas de implementação, e entender por que cada decisão foi tomada. O público-alvo são estudantes de graduação em computação que já conhecem o básico de Python; nenhum conhecimento prévio de pygame é necessário.

O texto foi escrito para ser lido com o código aberto ao lado. Os trechos citados estão no repositório público do projeto (<https://github.com/Joaofernandes-DEV/v2_jogoCobrinha>), e as capturas de tela mostram o jogo em funcionamento.

## O que é Computação Gráfica

Hughes *et al.* (2014) definem a Computação Gráfica, de forma ampla, como a área que trata da criação, da manipulação e da exibição de imagens por meio do computador. Na literatura nacional, Azevedo e Conci (2003) apresentam a área de forma semelhante e a relacionam a disciplinas vizinhas, como o processamento de imagens e a visão computacional. Marschner e Shirley (2021) dividem o campo em grandes áreas: modelagem (a descrição matemática das formas), renderização (a produção de imagens a partir dessa descrição), animação (a ilusão de movimento por sequências de imagens), interação com o usuário e processamento de imagens. Um jogo 2D simples toca em quase todas elas: há um modelo (a cobra, a grade e a comida), uma etapa de renderização (o desenho de cada quadro), animação (a comida que flutua, os textos que sobem e somem) e interação (o teclado e o mouse).

Uma distinção importante, que percorre todo este ebook, é entre o **modelo** e a **imagem**. O modelo é a descrição do que existe: "a cabeça da cobra está na coluna 9, linha 2". A imagem é uma matriz de pixels coloridos. A tarefa da CG é a ponte entre os dois, e boa parte da qualidade do Jogo da Cobrinha V2 vem de manter essa ponte explícita: as regras do jogo não sabem nada de pixels, e o desenho não decide nenhuma regra (capítulo 12).

## Breve história

A história da Computação Gráfica interativa costuma começar com o Sketchpad, sistema apresentado por Ivan Sutherland em 1963, no qual o usuário desenhava diretamente na tela com uma caneta óptica e o computador interpretava o desenho, mantendo restrições geométricas entre as partes (Sutherland, 1963). O Sketchpad trabalhava com uma tela vetorial: o feixe de elétrons percorria as linhas do desenho, uma a uma.

Pouco depois surgiram os algoritmos que permitiram desenhar em dispositivos discretos. O algoritmo de Bresenham (1965), criado para controlar um *plotter* digital, escolhe os pontos de uma grade que melhor aproximam um segmento de reta usando apenas soma, subtração e comparação de inteiros. Ele ainda é ensinado hoje porque resume a ideia central dos gráficos raster: o mundo contínuo precisa ser aproximado por uma grade finita.

Nas décadas de 1970 e 1980, a queda no preço da memória tornou viáveis os *frame buffers*, memórias que guardam a cor de cada pixel da tela. Com eles vieram os problemas que este ebook trata: como representar cores com poucos bits por pixel (Heckbert, 1982), como combinar imagens parcialmente transparentes (Porter; Duff, 1984) e como recortar o que fica fora da área visível (Sutherland; Hodgman, 1974). Em 1987, Lasseter mostrou como os princípios da animação tradicional se aplicavam às imagens geradas por computador, aproximando a CG do cinema (Lasseter, 1987).

Os jogos 2D, como o gênero Snake ao qual pertence o Jogo da Cobrinha, vivem exatamente nesse mundo raster: uma grade de pixels, imagens pequenas (*sprites*) copiadas para a tela a cada quadro, uma paleta de cores limitada e um laço que repete tudo dezenas de vezes por segundo.

## A ferramenta: Python e pygame-ce

O jogo foi escrito em Python 3.11 com a biblioteca pygame-ce (*pygame Community Edition*), uma camada sobre a SDL (*Simple DirectMedia Layer*), biblioteca em C que dá acesso portátil a janela, vídeo, teclado, mouse e áudio. O pygame-ce oferece superfícies (`pygame.Surface`, matrizes de pixels), cópia de blocos de imagem (`blit`), transformações geométricas simples (`pygame.transform`), fontes e som (Pygame-ce Developers, c2023). Ele não esconde o modelo raster, e por isso é uma boa ferramenta didática: quase todo conceito deste ebook corresponde a uma chamada visível no código.

## Como o ebook está organizado

O capítulo 2 conta a história do projeto, da V1 feita em grupo em 2025 até a versão 3.1.0, e apresenta a arquitetura do código. Os capítulos 3 a 13 tratam, cada um, de um conceito: gráficos raster e buffer duplo (3), sistemas de coordenadas (4), laço de jogo e passo de tempo fixo (5), o pipeline de desenho 2D (6), pixel art gerada por código (7), transformações geométricas (8), cor e quantização (9), transparência e composição (10), animação, com o estudo de caso do movimento interpolado que foi revertido (11), colisão, recorte e envolvimento de bordas (12) e interface e som (13). O capítulo 14 traz as considerações finais.

Ao final estão as referências, um glossário e o Apêndice A, com exercícios do tipo "experimente você mesmo" organizados por capítulo.

A apresentação segue as normas da ABNT para trabalhos acadêmicos (Associação Brasileira de Normas Técnicas, 2024), as citações seguem a NBR 10520 (Associação Brasileira de Normas Técnicas, 2023), no sistema autor-data, e as referências seguem a NBR 6023 (Associação Brasileira de Normas Técnicas, 2018).

<div class="caixa" markdown="1">
<p class="titulo-caixa">Convenções</p>

Trechos de código aparecem como "Código *n*", com o caminho do arquivo e as linhas exatas na fonte, abaixo do quadro. Nomes de funções, variáveis e arquivos aparecem em `fonte monoespaçada`. Os identificadores do projeto estão em português, por decisão registrada no briefing da V2 (item E6).
</div>
