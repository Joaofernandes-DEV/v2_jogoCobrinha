# Interface e multimídia

Os capítulos anteriores trataram do campo de jogo. Este trata do que está em volta dele: o HUD, os menus, os textos e o som. São assuntos que a CG compartilha com as áreas de interação humano-computador e de multimídia, e que no Jogo da Cobrinha seguem os mesmos princípios do resto do código: tudo é desenhado ou sintetizado por programa, a partir da mesma paleta e das mesmas regras.

## Interface desenhada por código

Na V1, menus, créditos, tela de fim de jogo e transições eram imagens feitas no Canva, com o texto embutido. Mudar uma opção exigia refazer a arte, e a navegação era só por teclas numéricas e letras soltas (briefing, seção 2.3). A V2 desenha toda a interface por código (item I1): os textos são renderizados com uma fonte, os menus são listas de itens navegáveis por setas, WASD e mouse, e o HUD é uma faixa própria de 50 px no topo, fora da área de jogo (item I2).

O @cod:hud mostra o começo do desenho do HUD: o fundo cinza-escuro, uma borda preta de 3 px separando-o do campo e os contadores de pontos e recorde. Os elementos seguintes dependem do estado da partida, como o modo de jogo, os power-ups ativos e o aviso de som desligado.

::: codigo #hud src/cobrinha/ui/hud.py 45-63
Desenho do HUD (`desenhar_hud`)
:::

O HUD recebe um objeto `DadosHud`, montado pela tela de jogo a partir da partida (capítulo 6). É o modelo e a visão de novo: o HUD não lê a partida diretamente, só os números que precisa mostrar. No modo Contra o tempo, a barra de progresso dá lugar a um relógio, que fica vermelho abaixo de 10 s (@fig:captura-contra-o-tempo).

::: figura captura-contra-o-tempo
Modo Contra o tempo: no centro do HUD, o relógio em vermelho, abaixo de 10 segundos, no lugar da barra de progresso
Fonte: captura gerada pelo autor (2026) com `docs/ebook/capturas.py`.
largura: 72%
:::

## Texto: fonte bitmap, cache e linha de base

Desenhar texto numa interface raster é rasterizar as formas das letras (os **glifos**) de uma fonte. O jogo usa a fonte VT323, de licença livre (SIL Open Font License), que imita o texto de terminais antigos e combina com a pixel art. A escolha tem uma história registrada no diário de bordo da Fase 3: a primeira fonte testada, a Press Start 2P, desenhava as maiúsculas acentuadas encolhidas ("NÍVEL" aparecia como "NíVEL") e não diferenciava Ó, Ô e Õ das minúsculas. Num jogo em português, isso era inaceitável. Três alternativas de licença livre foram comparadas lado a lado, e a VT323 foi a única com as maiúsculas acentuadas corretas e traços uniformes. O teste `test_fonte_tem_maiusculas_acentuadas_de_verdade` impede que o problema volte.

Três decisões do código de texto são de CG:

- **Sem suavização**: o texto é renderizado com `antialias=False` (@cod:texto, linha 15). As bordas ficam serrilhadas, como na pixel art, e o texto usa só a cor pedida, sem tons intermediários.
- **Cache**: rasterizar texto custa caro, e o HUD mostra os mesmos textos quadro após quadro. O decorador `lru_cache` guarda as últimas 256 combinações de texto, tamanho e cor, e o texto só é rasterizado de novo quando o valor muda (item D3 do briefing). Na V1, a fonte era recriada duas vezes por quadro.
- **Linha de base**: as maiúsculas acentuadas sobem acima da altura normal da fonte, e o pygame-ce aumenta a imagem do texto para cima para acomodá-las. Centralizada pelo topo, uma palavra com acento pareceria 3 px mais baixa que as outras. A função `_excesso_acima` mede, com as métricas dos glifos, quanto o texto passa do topo da fonte, e o desenho compensa esse valor, mantendo todas as palavras alinhadas pela **linha de base** (linhas 18 a 28).

::: codigo #texto src/cobrinha/ui/texto.py 11-28
Texto sem suavização, com cache e medida do excesso acima da fonte
:::

Um teste do projeto vai além: ele lê o código das telas, extrai todos os textos exibidos e confere se cada caractere gera pixels na fonte. O teste nasceu de um problema encontrado nas capturas da Fase 4: as setas "← →" informavam métricas, mas o glifo era vazio, e apareciam em branco na tela. O mesmo problema reapareceu na produção deste ebook, nos fluxogramas desenhados com a VT323, e foi resolvido da mesma forma: o gerador de figuras troca os símbolos sem desenho e falha se sobrar algum (`docs/ebook/figuras.py`, função `preparar`).

## Telas de transição

A contagem 3-2-1 antes de cada nível (@fig:captura-contagem) é um exemplo de como as peças dos capítulos anteriores se combinam numa tela de interface: ela é empilhada sobre a partida (capítulo 6), escurece o campo com um véu semitransparente (capítulo 10), escreve o nível e o nome da fase com a fonte do jogo e conta o tempo com o `dt` do laço (capítulo 5). O jogador pode pulá-la com Enter, Espaço ou um clique.

::: figura captura-contagem
Contagem antes do nível 2, empilhada sobre a partida, com o véu escuro e o nome da fase
Fonte: captura gerada pelo autor (2026) com `docs/ebook/capturas.py`.
largura: 65%
:::

## Som sintetizado por código

O som não é gráfico, mas é parte da experiência multimídia do jogo e segue a mesma filosofia dos sprites: os 15 arquivos WAV do jogo, entre efeitos e músicas, são **sintetizados** pelo script `ferramentas/gerar_sons.py`, só com a biblioteca padrão do Python.

### Amostragem

Um som digital é, como uma imagem raster, uma sequência de **amostras**: valores da pressão do ar medidos a intervalos regulares. A **taxa de amostragem** do jogo é de 22 050 amostras por segundo. Pelo teorema da amostragem, uma taxa *f*<sub>s</sub> só representa frequências até *f*<sub>s</sub> / 2, a frequência de Nyquist (Roads, 1996), aqui 11 025 Hz, suficiente para os sons simples de um jogo retrô. Cada amostra é gravada com 16 bits, em canal único (mono), pelo módulo `wave` da biblioteca padrão do Python.

O paralelo com o capítulo 3 é direto: a taxa de amostragem está para o som assim como a resolução está para a imagem, e o número de bits por amostra está para o som assim como o número de bits por canal de cor está para a imagem.

### Ondas e envelope

Os sons de jogos antigos (*chiptune*) eram produzidos por circuitos que geravam ondas simples. O gerador imita isso com duas formas de onda, definidas como funções da **fase** (a fração do ciclo em que a onda está): a onda quadrada, que vale +1 na primeira parte do ciclo e −1 na segunda, e a onda triangular, que sobe e desce linearmente (@cod:ondas).

::: codigo #ondas ferramentas/gerar_sons.py 23-58
Ondas quadrada e triangular, frequência das notas e tom com envelope
:::

A função `nota` usa a afinação temperada: cada semitom multiplica a frequência por 2<sup>1/12</sup>, a partir do lá central (A4) em 440 Hz. A função `tom` gera as amostras de uma nota com um **envelope** linear: o volume sobe do zero em 5 ms (ataque) e desce a zero nos últimos 30 ms (soltura), o que evita estalos no começo e no fim do som (Roads, 1996). A @fig:grafico-ondas mostra 10 ms das duas ondas com o envelope aplicado; os pontos marcam algumas das amostras.

::: figura grafico-ondas
Dez milissegundos das ondas quadrada e triangular a 440 Hz, com envelope e amostras a 22 050 Hz
Fonte: elaborada pelo autor (2026) com `docs/ebook/figuras.py`, reproduzindo as fórmulas de `ferramentas/gerar_sons.py`.
:::

### Volume medido, e não suposto

O diário de bordo registra um episódio instrutivo. Depois da Fase 3, o autor relatou que o áudio "não estava funcionando". O diagnóstico mostrou que o som tocava, mas baixo: a normalização do gerador só **reduzia** o volume quando o pico passava de 0,9, nunca aumentava, e, somada aos volumes padrão conservadores, deixava os sons cerca de 10 dB abaixo do ideal. A correção normaliza todos os sons para um pico de 0,89 (−1 dBFS), com intensidade relativa por som, e a lição ficou registrada: "mudanças de áudio são conferidas também pelo pico que chega ao Windows". É o equivalente sonoro de conferir as capturas de tela em vez de supor que o desenho está certo.

### Som ligado aos eventos

Os sons são disparados pelos eventos que a partida devolve a cada passo (capítulo 12). A tela de jogo tem uma tabela que associa cada evento a um efeito sonoro (`estados/jogando.py`, linhas 44 a 52): comer toca a mordida, bater toca a batida, concluir o nível toca a fanfarra. A música também reage ao jogo: cada fase tem sua faixa, a música pausa junto com o jogo e para "na hora" ao bater, antes mesmo da animação de morte. Como a partida só emite eventos e não conhece o áudio, esse comportamento pôde ser coberto por testes (`tests/test_musica.py`) sem nenhum dispositivo de som.

<div class="caixa" markdown="1">
<p class="titulo-caixa">Experimente</p>

Em `ferramentas/gerar_sons.py`, no efeito `"contagem"` (o bipe do 3-2-1), troque `q25` por `triangular` e regenere os sons com `python ferramentas/gerar_sons.py`. Compare o timbre: a onda quadrada tem muitos harmônicos e soa "áspera"; a triangular, com harmônicos mais fracos, soa mais suave. Desfaça a mudança com `git checkout -- ferramentas src/cobrinha/assets/sons`.
</div>
