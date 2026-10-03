Terceira versão do Jogo da Cobrinha: tudo o que a V2 tinha, agora com **power-ups**.

![Demonstração](https://raw.githubusercontent.com/Joaofernandes-DEV/v2_jogoCobrinha/v3.0.0/docs/demo.gif)

## Como jogar (Windows)

1. Baixe o **`Cobrinha.exe`** aqui embaixo, em *Assets*.
2. Dê dois cliques. Não precisa instalar Python nem nada.
3. Se o Windows mostrar "O Windows protegeu o computador" (SmartScreen), clique em **Mais informações → Executar assim mesmo**. Isso acontece com programas sem assinatura digital paga, como este.

Controles: setas ou WASD movem a cobra; Esc ou P pausa; M liga e desliga o som; o mouse funciona nos menus.

## Novidades em relação à V2

Às vezes, depois de comer, aparece um power-up. Ele fica 7 segundos no campo (pisca antes de sumir) e não dá pontos nem faz crescer, só aplica o efeito:

- **Câmera lenta** (fruta azul com relógio): a cobra anda na metade da velocidade por 5 s, e o campo fica azulado.
- **Pontos em dobro** (cereja dupla): por 8 s, cada maçã vale 2 pontos e a maçã dourada vale 10.
- **Encolher** (cogumelo): a cauda perde 3 segmentos na hora.

Os efeitos ativos aparecem no HUD com os segundos restantes, param na pausa e acabam ao trocar de fase. Cada power-up tem sprite e som próprios, gerados por código como o resto dos assets.

Também na V3: **João Pedro Sinhorini Silva** entra nos créditos como colaborador. O modo **Contra o tempo**, feito por ele, vem numa próxima versão.

## Por dentro

São 213 testes automatizados, CI no GitHub Actions (Linux e Windows) e o executável gerado por este mesmo workflow. Diário de bordo completo em [`LOG.md`](https://github.com/Joaofernandes-DEV/v2_jogoCobrinha/blob/v3.0.0/LOG.md).
