Reescrita completa do Jogo da Cobrinha, feito originalmente em 2025 para a disciplina de Computação Gráfica.

![Demonstração](https://raw.githubusercontent.com/Joaofernandes-DEV/v2_jogoCobrinha/v2.0.0/docs/demo.gif)

## Como jogar (Windows)

1. Baixe o **`Cobrinha.exe`** aqui embaixo, em *Assets*.
2. Dê dois cliques. Não precisa instalar Python nem nada.
3. Se o Windows mostrar "O Windows protegeu o computador" (SmartScreen), clique em **Mais informações → Executar assim mesmo**. Isso acontece com programas sem assinatura digital paga, como este.

Controles: setas ou WASD movem a cobra; Esc ou P pausa; M liga e desliga o som; o mouse funciona nos menus.

## Novidades em relação à V1

- **Pixel art nova**, desenhada em 25 × 25 px, com a cobra fazendo curvas de verdade.
- **3 fases com identidade:** Campo aberto, Pedras no caminho e Labirinto. A cobra acelera a cada maçã.
- **Maçã dourada:** +5 pontos, mas some em 5 segundos.
- **Dois modos:** Clássico (a borda mata) e Sem bordas (a cobra atravessa).
- **Recordes salvos:** top 5 de cada modo, com data.
- **Música diferente no menu e em cada fase**, efeitos sonoros retrô e mudo com a tecla M.
- **Menus por teclado e mouse**, pausa, contagem 3-2-1, tela de opções (volumes, tela cheia, efeitos visuais) e créditos.
- **Correção de todos os bugs da V1:** o jogo não fecha mais com erro, a grade está alinhada, a meia-volta não mata mais e o jogo não trava com o campo cheio.

## Por dentro

Código em Python 3.11 + pygame-ce, organizado em domínio (regras sem pygame), telas e interface. São 190 testes automatizados, CI no GitHub Actions (Linux e Windows), sprites e sons gerados por código e o executável gerado por este mesmo workflow. Diário de bordo completo em [`LOG.md`](https://github.com/Joaofernandes-DEV/v2_jogoCobrinha/blob/v2.0.0/LOG.md).
