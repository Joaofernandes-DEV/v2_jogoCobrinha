# Apêndice A – Experimente você mesmo

Os exercícios abaixo usam o próprio repositório do jogo. Para prepará-lo, siga a seção "Rodar pelo código-fonte" do README: clonar o repositório, criar um ambiente virtual e instalar com `pip install -e ".[dev]"`. Antes de cada exercício, crie uma branch (`git switch -c estudo/nome`), e ao final volte à `main` e apague-a. Assim nenhuma mudança se perde nem fica para trás.

## Capítulos 3 e 4: raster e coordenadas

1. Rode o jogo com `python -m cobrinha --debug` e observe o FPS no canto inferior direito. Em seguida, mude `FPS` em `src/cobrinha/config.py` para 20 e jogue de novo. A cobra continua na mesma velocidade? Por quê? (Releia o capítulo 5.)
2. Mude `ALTURA_HUD` para 100 em `config.py`. Quantas linhas de código precisaram mudar para o campo inteiro descer? O que isso diz sobre a função `celula_para_pixel`?
3. Calcule quantos bytes ocupa um quadro do jogo com 4 bytes por pixel e quanto ocuparia em tela cheia numa resolução de 1920 × 1080. Por que o jogo continua desenhando em 800 × 600 mesmo em tela cheia?

## Capítulo 5: laço de jogo e passo fixo

4. Em `tests/test_partida.py`, escreva um teste que crie uma `Partida`, chame `atualizar(0.124)` e confira que a cobra não andou; depois chame `atualizar(0.002)` e confira que ela andou uma célula. Qual é o intervalo do passo no nível 1?
5. Chame `atualizar(5.0)` (um travamento de 5 s) e conte quantos passos a cobra deu. Relacione o resultado com `MAX_PASSOS_POR_QUADRO`.

## Capítulo 6: pipeline de desenho

6. Em `EstadoJogando.desenhar`, mova a linha que desenha a cobra para antes do fundo do campo. O que acontece? Explique com o algoritmo do pintor.
7. Comente a linha que desenha os textos flutuantes e coma uma maçã. Depois, recoloque-a antes da cobra. Em qual posição o "+1" fica mais legível?

## Capítulos 7 e 8: pixel art e transformações

8. Mude `ESPESSURA = 17` em `ferramentas/gerar_sprites.py` para 13, regenere os sprites e jogue. A curva continua se encaixando no corpo reto? Por quê?
9. Na função `comida`, troque `raio * 0.9` por `raio * 0.3` na condição da sombra. Regenere e compare. Que reta define a sombra agora?
10. Num terminal Python, gire um sprite em 45° com `pygame.transform.rotate` e compare o tamanho com o original. Salve o resultado e examine as bordas ampliadas.

## Capítulos 9 e 10: cor e composição

11. Abra `docs/ebook/figuras/captura-jogando.png` com a Pillow e quantize-a para 16 cores com e sem pontilhado (`dither`). Compare os resultados com uma lupa.
12. Calcule a cor de um pixel da grama escura (124, 178, 66) sob o véu azul da câmera lenta e confira com a captura `captura-camera-lenta.png`, no pixel (35, 70).
13. Mude `OPACIDADE_VEU_LENTO` em `src/cobrinha/estados/jogando.py` para 120. O efeito fica mais claro? O campo continua legível?

## Capítulo 11: animação

14. Troque `round(math.sin(...))` por `math.sin(...) * 3` em `_desenhar_flutuando`. O que acontece com a nitidez da maçã? (Dica: o `blit` aceita posições fracionárias?)
15. Mude a curva de opacidade dos textos flutuantes de `1 - progresso**2` para `1 - progresso`. Qual das duas deixa o "+1" mais legível?
16. Recupere a versão com movimento interpolado (`git switch --detach ddb474b`) e jogue no nível 3. Anote o momento em que a maçã some e onde está a cabeça desenhada nesse instante.

## Capítulos 12 e 13: colisão, interface e som

17. Escreva um teste para a regra da cauda segura em `Cobra.colidiria`, com e sem crescimento pendente.
18. No modo Sem bordas, saia pela borda de cima. Qual linha a cabeça ocupa no passo seguinte? Confira com `Grade.envolver`.
19. Em `ferramentas/gerar_sons.py`, troque a onda do bipe da contagem e regenere os sons. Descreva a diferença de timbre.
