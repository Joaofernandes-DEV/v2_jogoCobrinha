Novo modo de jogo: **Contra o tempo**, feito pelo colaborador João Pedro Sinhorini Silva.

## Como jogar (Windows)

1. Baixe o **`Cobrinha.exe`** aqui embaixo, em *Assets*.
2. Dê dois cliques. Não precisa instalar Python nem nada.
3. Se o Windows mostrar "O Windows protegeu o computador" (SmartScreen), clique em **Mais informações → Executar assim mesmo**. Isso acontece com programas sem assinatura digital paga, como este.

Controles: setas ou WASD movem a cobra; Esc ou P pausa; M liga e desliga o som; o mouse funciona nos menus.

## Novidades em relação à v3.0.0

No menu, escolha **MODO: < CONTRA O TEMPO >** (com `←` e `→`):

- O relógio começa em **60 s**. Cada maçã devolve **+3 s** e a maçã dourada **+5 s** (o relógio nunca passa de 99 s).
- Não há meta de comidas: o nível escolhido define só o mapa e a velocidade. É uma corrida de pontos.
- Abaixo de 10 s o relógio fica vermelho. Quando zera, a partida termina em **TEMPO ESGOTADO!**. Bater também encerra.
- O modo tem o próprio top 5 na tela de recordes, que agora circula pelos 3 modos nos dois sentidos.
- Os power-ups da v3.0.0 também valem aqui. Com pontos em dobro, cada maçã vale 2 pontos (os segundos ganhos não dobram).

Os recordes e opções salvos nas versões anteriores continuam valendo.

## Por dentro

São 240 testes automatizados, CI no GitHub Actions (Linux e Windows) e o executável gerado por este mesmo workflow. Diário de bordo completo em [`LOG.md`](https://github.com/Joaofernandes-DEV/v2_jogoCobrinha/blob/v3.1.0/LOG.md).
