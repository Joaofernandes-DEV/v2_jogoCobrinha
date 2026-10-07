# Considerações finais

Este ebook percorreu os conceitos centrais da Computação Gráfica 2D usando como fio condutor um projeto real, o Jogo da Cobrinha, em suas três versões. O @qua:resumo-conceitos resume a correspondência entre cada conceito e o lugar do código em que ele aparece.

::: quadro #resumo-conceitos
Conceitos de Computação Gráfica e onde aparecem no Jogo da Cobrinha
Fonte: elaborado pelos autores (2026).
| Conceito | Onde aparece no jogo | Capítulo |
|---|---|---|
| Raster, framebuffer e buffer duplo | `pygame.Surface`, `Jogo._desenhar` e `display.flip()` | 3 |
| Sistemas de coordenadas e transformação afim | Grade de 32 × 22 células e `celula_para_pixel` | 4 |
| Laço de jogo e passo de tempo fixo | `Jogo.executar` e o acumulador de `Partida.atualizar` | 5 |
| Algoritmo do pintor, blit e camadas | `EstadoJogando.desenhar`, fundo pré-renderizado e pilha de telas | 6 |
| Formas implícitas e rasterização | `ferramentas/gerar_sprites.py` (maçã, curva, contorno) | 7 |
| Rotação e escala de imagens raster | Peças giradas em 90°, vizinho mais próximo e `pygame.SCALED` | 8 |
| RGB, paleta e quantização | Classe `Paleta` e o corte pela mediana no GIF | 9 |
| Canal alfa e operador *over* | Véus, fade de transição e textos flutuantes | 10 |
| Animação por tempo e interpolação | Flutuação, pisca-pisca e o movimento interpolado revertido | 11 |
| Colisão, recorte e envolvimento | Conjunto de células ocupadas, `set_clip` e `Grade.envolver` | 12 |
| Interface e som | HUD, fonte VT323 e síntese de ondas em `gerar_sons.py` | 13 |
:::

Três ideias atravessam todos os capítulos.

A primeira é a **separação entre modelo e imagem**. O jogo nunca guarda a posição da cobra em pixels, e as regras nunca dependem de como algo é desenhado. Essa separação, proposta no briefing da V2 como resposta direta aos bugs da V1, é o que permitiu testar o jogo sem janela, gravar o GIF de demonstração com um piloto automático e experimentar o movimento interpolado sem risco para as regras.

A segunda é **fazer o trabalho uma vez**. O fundo é pré-renderizado, as rotações das peças são calculadas ao criar a tela, as imagens são convertidas para o formato da tela ao carregar, e os textos ficam em cache. Em todos os casos, a técnica é trocar um pouco de memória por tempo de quadro, uma das trocas mais comuns da CG interativa.

A terceira é **gerar por código**. Sprites, sons e o GIF de demonstração são produzidos por scripts versionados no repositório. Isso torna o resultado reproduzível e transforma cada asset em documentação de como ele foi feito, o que é especialmente valioso num trabalho acadêmico: quem quiser entender um sprite pode ler a função que o desenha.

O estudo de caso do movimento interpolado mostrou, por fim, que conhecer a teoria não substitui o julgamento de projeto. A interpolação é uma técnica correta e bem fundamentada na literatura, e foi bem implementada; mesmo assim, para um Snake a 8 passos por segundo, com pixel art e jogabilidade discreta, o atraso visual e a perda de estilo pesaram mais. O diário de bordo, ao registrar a tentativa e a volta, transformou uma reversão em aprendizado.

## Trabalhos futuros

O próprio backlog do projeto, na seção 8.4 do briefing, aponta caminhos que estenderiam os temas deste ebook: partículas e tremor de tela (animação e efeitos), uma versão para navegador com pygbag (portabilidade do pipeline), um editor de níveis (interação e modelagem) e o remapeamento de teclas (interface e acessibilidade). Do ponto de vista da CG, um exercício interessante seria implementar à mão, sem a SDL, operações que o jogo hoje delega à biblioteca, como a rotação de uma imagem por um ângulo qualquer, com vizinho mais próximo e com interpolação bilinear, ou o operador *over* com alfa pré-multiplicado, e comparar os resultados com os do pygame-ce.
