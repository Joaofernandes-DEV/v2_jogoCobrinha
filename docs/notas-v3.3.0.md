Chegou o **modo Duelo**: de 2 a 4 pessoas no mesmo campo, cada uma com a sua cobra, pelo teclado ou pelo controle.

## Como jogar (Windows)

1. Baixe o **`Cobrinha.exe`** aqui embaixo, em *Assets*.
2. Dê dois cliques. Não precisa instalar Python nem nada.
3. Se o Windows mostrar "O Windows protegeu o computador" (SmartScreen), clique em **Mais informações → Executar assim mesmo**. Isso acontece com programas sem assinatura digital paga, como este.

Teclado: setas ou WASD movem a cobra; Esc ou P pausa; M liga e desliga o som; o mouse funciona nos menus.

## Novidades em relação à v3.2.0

Escolha **DUELO** no menu. Na tela **Quem joga?**, cada pessoa entra de um jeito:

| Quem | Como entra | Como joga |
|------|------------|-----------|
| Lado esquerdo do teclado | `W` `A` `S` `D` | `W` `A` `S` `D` |
| Lado direito do teclado | uma seta | setas |
| Cada controle (DualSense ou outro) | ✕ | direcional ou analógico |

Com 2 a 4 jogadores, `Enter` (ou o ✕ de quem já entrou) começa. As cobras são verde, azul, amarela e vermelha, na ordem de chegada.

- **Regras:** bater na borda, numa pedra, em si mesmo ou em outra cobra elimina, e a cobra eliminada some do campo. Duas cabeças na mesma célula, ou trocando de lugar, eliminam as duas. Vence a rodada quem sobrar; se todos baterem no mesmo passo, é empate.
- **Rodadas:** entre uma rodada e outra, o placar mostra as vitórias de cada um. Quem fizer **3 vitórias** é o campeão.
- **Modos:** o item MODO do menu vale no duelo.
  - **Clássico:** a borda elimina.
  - **Sem bordas:** a cobra atravessa a borda.
  - **Contra o tempo:** cada rodada tem 60 s, e vence quem tiver mais pontos quando o tempo acabar.
- **Power-ups disputados:**
  - **câmera lenta:** deixa os adversários na metade da velocidade por 5 s;
  - **cogumelo:** corta 3 segmentos da cauda dos adversários;
  - **pontos em dobro:** valem só para quem pegou, e só aparecem no Contra o tempo.
- **Controles:**
  - cada controle acende na cor da cobra do seu jogador e só vibra com o que acontece com ele;
  - se o controle de um jogador desconectar, o duelo para até ele ser reconectado e apertar ✕.

O duelo não entra nos recordes. Os modos de 1 jogador continuam iguais, e os recordes e opções salvos nas versões anteriores continuam valendo.

## Por dentro

São 445 testes automatizados, CI no GitHub Actions (Linux e Windows) e o executável gerado por este mesmo workflow. Diário de bordo completo em [`LOG.md`](https://github.com/Joaofernandes-DEV/v2_jogoCobrinha/blob/v3.3.0/LOG.md).
