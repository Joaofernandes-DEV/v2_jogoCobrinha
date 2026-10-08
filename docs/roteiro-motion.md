# Roteiro do anúncio em motion design (40 s)

Roteiro e prompt para criar um anúncio em motion design do Jogo da Cobrinha, em uma sessão separada do Claude. O anúncio não tem narração: a história é contada por tipografia cinética e pelos sons do próprio jogo.

## Como usar

1. Abra a nova sessão **na pasta raiz do projeto**, para ela alcançar os assets da V2 e as telas da V1 (`Py_JogoDaCobrinha/`, clone da V1 ignorado pelo git).
2. Copie o bloco da seção [Prompt completo](#prompt-completo) e cole como primeira mensagem.
3. Revise a prévia cena a cena antes de pedir a renderização final.

## Resumo

| Item | Valor |
|---|---|
| Duração | 40 s |
| Formato | 16:9, 1920×1080, 60 fps (versão vertical 9:16 opcional) |
| Estilo | Pixel art animada com tipografia cinética, movimento em degraus de grade |
| Som | Efeitos e trilhas do próprio jogo, sem narração |
| Fonte | VT323 |
| Paleta | Fundo `#14101A`, texto `#F0ECE4`, verdes `#468C3C` e `#76BA48`, destaque `#F6CC46`, alerta `#C83434` |

## Linha do tempo

| Tempo | Cena | Texto na tela |
|---|---|---|
| 0:00–0:03 | Gancho | "Lembra da cobrinha?" |
| 0:03–0:08 | A V1 | "V1 · 2025 · em grupo", "Ficou aquém." |
| 0:08–0:12 | A virada | "Agora, a V2.", "Eu + João Pedro." |
| 0:12–0:15,5 | Pixel art e 3 níveis | "3 níveis" |
| 0:15,5–0:18,5 | Maçã dourada | "Maçã dourada: 5 s" |
| 0:18,5–0:21,5 | Sem bordas | "Modo sem bordas" |
| 0:21,5–0:25 | Power-ups | "3 power-ups" |
| 0:25–0:28,5 | Contra o tempo | "Contra o tempo, por João Pedro" |
| 0:28,5–0:31 | Música e recordes | "Música por fase · Recordes" |
| 0:31–0:36 | Bastidores | "240+ testes · CI · .exe pronto" |
| 0:36–0:40 | Fechamento | "Baixe grátis · Windows" e o link do repositório |

## Prompt completo

```text
Crie um anúncio em motion design de 40 s (1920x1080, 60 fps) para o Jogo da Cobrinha V2.
Siga o roteiro abaixo. Use os assets reais do projeto em:
C:\Users\joaov\Documents\Estudos\UNIP\ProjetoExtensao\V2_JogoCobrinha

ASSETS
- Sprites da V2: src/cobrinha/assets/imagens/ (PNG 25x25; ampliar sempre com nearest-neighbor, nunca suavizar).
  Usados: cabeca.png, corpo_reto.png, corpo_curva.png, cauda.png, comida.png, comida_dourada.png, parede.png, power_camera_lenta.png, power_pontos_em_dobro.png, power_encolher.png.
- Fonte: src/cobrinha/assets/fontes/VT323-Regular.ttf
- Sons e trilhas: src/cobrinha/assets/sons/ (comer, bater, nivel, menu_mover, bonus, power_up, contagem, vitoria, musica_menu, musica_fase1, musica_fase2, musica_fase3).
- Paleta: classe de cores em src/cobrinha/config.py.
- V1 (jogo antigo, só como referência visual da cena 2): Py_JogoDaCobrinha/Jogo da cobrinha/assets/
  Telas: Inicio.png, nivel1.png, nivel2.png, nivel3.png, teladeescolha.png, game over.png (800x600, 4:3).
  Não esticar para 16:9: mostrar numa moldura centralizada, com o fundo #14101A nas laterais.
  NÃO usar creditos.png (tem nomes de todo o grupo da V1) e não colocar nomes do grupo da V1 na tela.

ROTEIRO CENA A CENA (40 s no total)

CENA 1 | 0:00-0:03 | Gancho
Tela escura (#14101A). A cabeça da cobra entra deslizando em passos de grade de 25 px (movimento em degraus, não suave) e come a maçã. Texto na tela: "Lembra da cobrinha?". Som: comer.wav.

CENA 2 | 0:03-0:08 | A V1
Dentro de uma moldura 4:3 centralizada, mostrar as telas reais da V1 em cortes rápidos (cerca de 1 s cada): Inicio.png (floresta e cobra verde grande), nivel1.png (galáxia) e game over.png. Sobre elas, o texto "V1 · 2025 · em grupo". Em seguida, glitch e queda de saturação, e a tela "quebra" em pixels com o texto "Ficou aquém.". Som: bater.wav no momento da quebra.

CENA 3 | 0:08-0:12 | A virada
Os pixels da tela quebrada da V1 se recompõem na grade de 25 px da V2 e formam o título. A cobra desenha o "V2" andando pela grade. Texto: "Agora, a V2." e depois "Eu + João Pedro.". Som: nivel.wav.

CENA 4 | 0:12-0:15,5 | Pixel art e 3 níveis
Três mini-mapas surgem em sequência: campo aberto, pedras no caminho e labirinto (use parede.png para as pedras e os corredores). Texto: "3 níveis". Som: menu_mover.wav, uma vez por mapa.

CENA 5 | 0:15,5-0:18,5 | Maçã dourada
A maçã dourada (comida_dourada.png) pisca e um contador regressivo roda de 5 a 0. Texto: "Maçã dourada: 5 s". Som: bonus.wav.

CENA 6 | 0:18,5-0:21,5 | Sem bordas
A cobra sai pela borda direita e entra pela esquerda, deixando um rastro. Texto: "Modo sem bordas".

CENA 7 | 0:21,5-0:25 | Power-ups
Os três sprites (power_camera_lenta.png, power_pontos_em_dobro.png, power_encolher.png) entram com "pop" escalonado e leve overshoot. A cena fica azulada durante a câmera lenta. Texto: "3 power-ups". Som: power_up.wav.

CENA 8 | 0:25-0:28,5 | Contra o tempo
Um relógio grande conta de 60 até 9. Abaixo de 10 ele fica vermelho (#C83434). Texto: "Contra o tempo, por João Pedro". Som: contagem.wav.

CENA 9 | 0:28,5-0:31 | Música e recordes
Uma onda sonora em pixel art pulsa no ritmo da trilha, e uma tabela de top 5 sobe com os números rolando. Texto: "Música por fase · Recordes". Som: trecho de musica_fase3.wav.

CENA 10 | 0:31-0:36 | Bastidores
Contadores sobem: 240+ testes, selo de CI verde (Linux + Windows) e ícone de .exe. Texto: "240+ testes · CI · .exe pronto".

CENA 11 | 0:36-0:40 | Fechamento
A cobra forma o logo e a caixa de download pisca em amarelo (#F6CC46). Texto: "Baixe grátis · Windows" e "github.com/Joaofernandes-DEV/v2_jogoCobrinha". Som: vitoria.wav.

DIRETRIZES GERAIS DE MOVIMENTO
- Tudo no ritmo da grade: movimentos em degraus de 25 px, como no jogo.
- Easing: ease-out curto (150-250 ms) nas entradas de texto; "pop" com leve overshoot nos sprites.
- Trocas de cena no beat da trilha. Trilha de fundo: musica_menu.wav ou musica_fase1.wav, em volume baixo, sob os efeitos.
- No máximo um texto principal por cena.
- Sem narração: só tipografia cinética e os sons do jogo.
- Paleta: fundo #14101A, texto #F0ECE4, verdes #468C3C e #76BA48, destaque #F6CC46, alerta #C83434. Fonte VT323.
- Sprites sempre ampliados com nearest-neighbor, nunca suavizados.

ENTREGA
- Primeiro, escolha a ferramenta (por exemplo HTML/CSS/JS animado com gravação, ou Remotion) e justifique em uma linha.
- Entregue o projeto-fonte e um MP4 1920x1080 a 60 fps com o áudio já mixado. Se a ferramenta não exportar MP4 sozinha, explique como exportar.
- Mostre uma prévia cena a cena e espere minha aprovação antes da renderização final.
- Salve tudo fora de src/ e de tests/ (por exemplo em docs/motion/), sem alterar o código do jogo.
```

## Fatos usados no anúncio

Todos os números e recursos vêm do repositório, na versão 3.1.0:

- **3 níveis:** campo aberto, pedras no caminho e labirinto.
- **Maçã dourada:** some em 5 s e vale +5 pontos.
- **Modo sem bordas:** a cobra atravessa a borda e sai do outro lado.
- **Power-ups:** câmera lenta, pontos em dobro e encolher.
- **Contra o tempo:** relógio de 60 s, fica vermelho abaixo de 10 s; modo feito por João Pedro Sinhorini Silva.
- **Bastidores:** mais de 240 testes automatizados (244 na última execução), CI no GitHub Actions (Linux e Windows) e `Cobrinha.exe` na release.
