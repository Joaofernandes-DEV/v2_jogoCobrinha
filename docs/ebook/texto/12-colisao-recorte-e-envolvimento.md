# Colisão, recorte e envolvimento de bordas

Este capítulo reúne três assuntos que, no Jogo da Cobrinha, ficam na fronteira entre a geometria e as regras do jogo: a **detecção de colisão**, o **recorte** (*clipping*) do que não deve aparecer e o **envolvimento** das bordas no modo Sem bordas. Os três dependem da decisão arquitetural mais importante do projeto, a separação entre o modelo do jogo e a sua visão, e é por ela que o capítulo começa.

## Modelo e visão

Krasner e Pope (1988) descrevem o paradigma *Model-View-Controller* (MVC), usado no Smalltalk-80, como uma divisão em três partes: objetos que tratam do domínio da aplicação (o modelo), objetos que exibem o estado desse domínio (a visão) e objetos que tratam a interação do usuário (o controlador). A ideia central é que o modelo não conheça a visão: ele pode ser exibido de várias formas, ou de nenhuma, sem mudar.

O Jogo da Cobrinha aplica essa ideia de forma direta (decisão E4 do briefing). O pacote `dominio/` é o modelo: grade, cobra, comida, níveis, power-ups, progresso e partida, sem nenhum `import pygame`. As telas em `estados/` fazem o papel de controlador, traduzindo teclas em comandos (`partida.virar(direcao)`), e também orquestram a visão, que mora em `ui/` (@fig:diagrama-arquitetura, no capítulo 2). A partida não sabe o que é um pixel, uma cor ou um sprite; a interface não decide quando a cobra morre.

Essa separação tem três consequências práticas, todas visíveis no projeto:

- **Testabilidade**: a maior parte dos 240 testes roda sem janela. `tests/test_partida.py` simula partidas aleatórias de 500 passos e confere invariantes a cada passo; `tests/test_niveis.py` usa uma busca em largura para provar que nenhum mapa de pedras tem área fechada.
- **Experimentação segura**: o movimento interpolado (capítulo 11) foi implementado e removido mexendo quase só na interface.
- **Reuso**: o piloto automático que grava o GIF de demonstração joga com o mesmo modelo, sem duplicar regras.

## Detecção de colisão

Em jogos com objetos de formas e posições contínuas, a detecção de colisão é um problema geométrico complexo. Ericson (2005) organiza as técnicas em fases: uma fase ampla (*broad phase*), que descarta rapidamente os pares de objetos que não podem colidir, muitas vezes com grades espaciais ou volumes envolventes simples, como caixas alinhadas aos eixos (AABB, *axis-aligned bounding boxes*); e uma fase estreita (*narrow phase*), que testa a geometria exata dos pares restantes.

Num jogo em grade, todo esse aparato se reduz a uma pergunta simples: **a célula de destino está ocupada?** Como as posições são inteiras e cada objeto ocupa exatamente uma célula, não há sobreposição parcial, tolerância numérica ou ordem de testes a escolher. A V1, que trabalhava em pixels, criava um `pygame.Rect` por segmento a cada passo para testar colisão; a V2 usa um conjunto (`set`) de células ocupadas, em que testar pertinência custa O(1) em média (item D4 do briefing).

O @cod:colidiria mostra a colisão da cobra com o próprio corpo e o movimento que a mantém consistente.

::: codigo #colidiria src/cobrinha/dominio/cobra.py 81-98
Colisão com o próprio corpo e avanço da cobra (`Cobra.colidiria` e `Cobra.avancar`)
:::

O detalhe da linha 87 é uma regra fina do Snake: a célula da cauda é segura quando a cobra não está crescendo, porque a cauda sai dali no mesmo passo em que a cabeça entra. Sem essa regra, a cobra morreria ao "perseguir" a própria cauda, o que contraria o jogo clássico. Para que isso funcione, `avancar` retira a cauda antes de inserir a nova cabeça (linhas 92 a 98). O corpo é um `deque`, em que inserir na cabeça e retirar da cauda custam O(1), e o conjunto `_ocupadas` acompanha o `deque` para responder às perguntas de colisão.

## Um passo da partida

O método `Partida.passo` junta todas as regras de colisão e consumo de itens (@cod:passo). A @fig:fluxo-passo-partida mostra o mesmo método como fluxograma, incluindo as regras de `_comer`.

::: codigo #passo 270f2fc:src/cobrinha/dominio/partida.py 161-183
Um passo da partida: movimento, colisão e itens (`Partida.passo`)
:::

::: figura fluxo-passo-partida
Fluxograma de um passo da partida: mover, colidir, comer, pegar power-up, vencer ou concluir o nível
Fonte: elaborada pelos autores (2026) com base em `src/cobrinha/dominio/partida.py`.
:::

Três observações ajudam a ler o código.

A colisão é testada **antes** de mover (linhas 168 a 174): primeiro se calcula a nova cabeça, depois se pergunta se ela é válida, e só então a cobra avança. Assim, ao bater, a cobra fica parada na posição anterior, e o quadro de "game over" mostra a cabeça encostada no obstáculo, e não dentro dele.

O método devolve um `Evento` (`MOVEU`, `COMEU`, `BATEU` etc.). É assim que o modelo informa a visão sem conhecê-la: a tela de jogo usa os eventos para tocar sons, criar textos flutuantes e parar a música, mas a partida não sabe que nada disso existe.

O fim por tempo, no modo Contra o tempo, não aparece aqui: ele é verificado em `atualizar`, depois dos passos do quadro (capítulo 5), porque depende do relógio, e não do movimento.

## A entrada também é modelo: a fila de direções

O bug B3 da V1 era uma colisão injusta causada pela entrada. A direção nova era comparada com a direção atual da cobra, que mudava a cada tecla. Andando para a direita, se o jogador apertasse ↑ e ← rapidamente, dentro do mesmo passo, a primeira tecla mudava a direção para cima e a segunda, comparada com "cima", era aceita, e a cobra virava para a esquerda, dentro do próprio pescoço.

A V2 resolve isso no modelo, com uma fila de até dois comandos, em que cada comando é validado contra o **último já enfileirado** (`Cobra.virar`, em `dominio/cobra.py`, linhas 60 a 73). As duas teclas viram duas curvas seguidas, uma em cada passo. A correção é coberta por testes, sem janela.

## Recorte (*clipping*)

**Recorte** é a operação de descartar as partes de uma primitiva que ficam fora de uma região, normalmente a área visível. Sutherland e Hodgman (1974) apresentaram um algoritmo clássico para recortar polígonos contra uma janela convexa: o polígono é recortado contra cada borda da janela, uma de cada vez, e a saída de cada etapa é a entrada da seguinte.

Em gráficos raster, o recorte também acontece no nível dos pixels. Todo `blit` do pygame-ce é recortado automaticamente aos limites da superfície de destino, e cada superfície tem ainda uma **área de recorte** configurável com `set_clip`, que `blit` e `fill` respeitam (Pygame-ce Developers, c2023). Desenhar fora da área não é um erro: os pixels simplesmente não são escritos.

O jogo atual quase não precisa disso, porque tudo é desenhado em células inteiras dentro do campo. A versão com movimento interpolado precisava, e o @cod:recorte, recuperado do histórico do Git, mostra como.

::: codigo #recorte e22164c:src/cobrinha/ui/pecas.py 140-158
Recorte ao campo e desenho dos dois lados da borda (versão removida com o movimento interpolado)
:::

Um segmento que desliza para fora da borda direita, no modo Sem bordas, precisa aparecer em parte na direita e em parte na esquerda do campo. O método faz isso desenhando o mesmo sprite uma segunda vez, deslocado de uma largura (ou altura) do campo, quando ele passa da borda direita ou da inferior, e até uma quarta vez no canto (linhas 151 a 157). Para que as partes excedentes não invadam o HUD nem saiam do campo, define uma área de recorte igual ao retângulo do campo (linha 150), restaurando a anterior no fim (linha 158). É o recorte por região retangular, a forma mais simples do problema estudado por Sutherland e Hodgman (1974), feito pela SDL no momento da cópia dos pixels.

## Envolvimento de bordas: o modo Sem bordas

No modo Sem bordas, a cobra que sai por um lado do campo entra pelo lado oposto. Topologicamente, o campo deixa de ser um retângulo e passa a ser um **toro**, a superfície de uma rosquinha, em que as bordas opostas estão coladas. No modelo, isso é uma linha de código, mostrada no @cod:envolver.

::: codigo #envolver src/cobrinha/dominio/grade.py 49-54
Teste de pertinência e envolvimento das bordas (`Grade.contem` e `Grade.envolver`)
:::

O operador `%` (resto da divisão) do Python devolve sempre um valor entre 0 e o divisor menos 1, mesmo para números negativos: −1 % 32 = 31. Por isso, a mesma expressão trata a saída pela direita (coluna 32 vira 0) e pela esquerda (coluna −1 vira 31). Na `Partida.passo`, o envolvimento acontece logo depois do cálculo da nova cabeça, e só no modo Sem bordas (`partida.py`, linhas 165 e 166). Nos outros modos, a posição fora do campo falha no teste `contem` e a cobra bate. A @fig:diagrama-envolvimento ilustra o caso numa grade pequena.

::: figura diagrama-envolvimento
Envolvimento de bordas numa grade de 10 × 6: a cabeça em (9, 2) indo para a direita aparece em (0, 2)
Fonte: elaborada pelos autores (2026).
:::

O desenho também precisa saber do envolvimento. Para escolher a peça e a rotação de cada segmento (capítulo 8), `classificar_pecas` calcula a direção entre segmentos vizinhos, e dois vizinhos em lados opostos do campo estão, numericamente, a 31 colunas de distância. A função `direcao_entre` (`ui/pecas.py`, linhas 68 a 80) trata esse salto como um passo no sentido contrário, e a cobra é desenhada corretamente atravessando a borda, como mostra a @fig:captura-sem-bordas.

::: figura captura-sem-bordas
Modo Sem bordas: a cobra atravessa a borda direita e continua pela esquerda do campo
Fonte: captura de tela do jogo, elaborada pelos autores (2026).
largura: 72%
:::

## Sorteio da comida sem laço cego

Uma última "colisão" é a da comida com o que já ocupa o campo. A V1 sorteava posições ao acaso até achar uma livre, e com o campo cheio esse laço nunca terminava (B7). A V2 sorteia diretamente entre as células livres (`dominio/comida.py`, linhas 9 a 19) e, se não houver nenhuma, devolve `None`, que a partida trata como vitória. O custo é percorrer as 704 células da grade uma vez por comida, desprezível perto dos 16,7 ms de um quadro.

<div class="caixa" markdown="1">
<p class="titulo-caixa">Experimente</p>

Em `tests/test_cobra.py`, escreva um teste que crie uma cobra de 4 segmentos em formato de "U" e confira que `colidiria` devolve `False` para a célula da cauda. Depois chame `crescer()` e confira que a mesma célula passa a ser uma colisão. Rode `pytest tests/test_cobra.py`.
</div>
