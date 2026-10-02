"""Constantes globais: janela, grade, tempo e paleta de cores.

Toda medida em pixels deriva da grade (ver seção 8.2 do briefing):
32 × 22 células de 25 px + faixa de HUD de 50 px = janela de 800 × 600.
"""

from typing import Final

Cor = tuple[int, int, int]

TITULO: Final = "Jogo da Cobrinha V2"

# Grade
TAMANHO_CELULA: Final = 25
COLUNAS: Final = 32
LINHAS: Final = 22

# Janela
ALTURA_HUD: Final = 50
LARGURA_JANELA: Final = COLUNAS * TAMANHO_CELULA
ALTURA_JANELA: Final = ALTURA_HUD + LINHAS * TAMANHO_CELULA

# Tempo
FPS: Final = 60
DURACAO_FADE: Final = 0.25  # segundos do fade de entrada ao trocar de tela (I7)

# Áudio (volumes de 0 a 1; ajustáveis na tela de opções da Fase 4)
FREQUENCIA_AUDIO: Final = 22_050
VOLUME_EFEITOS: Final = 0.6
VOLUME_MUSICA: Final = 0.35

# Jogabilidade
TAMANHO_INICIAL_COBRA: Final = 3
# Comandos de direção guardados à frente do movimento (buffer, J1 do briefing).
LIMITE_FILA_DIRECOES: Final = 2
# Teto de passos recuperados num único quadro, para a cobra não "teleportar"
# depois de um travamento (ex.: arrastar a janela).
MAX_PASSOS_POR_QUADRO: Final = 3


class TamanhoFonte:
    """Tamanhos da fonte pixel (VT323), escolhidos entre os que deixam os traços uniformes."""

    MINIMO: Final = 20
    PEQUENO: Final = 24
    MEDIO: Final = 32
    GRANDE: Final = 40
    TITULO: Final = 48
    ENORME: Final = 80
    GIGANTE: Final = 100


class Paleta:
    """Paleta única do jogo (até 16 cores), usada pelos sprites e pela interface."""

    PRETO: Final[Cor] = (20, 16, 26)
    CINZA_ESCURO: Final[Cor] = (46, 42, 58)
    CINZA: Final[Cor] = (98, 94, 110)
    CINZA_CLARO: Final[Cor] = (170, 166, 178)
    BRANCO: Final[Cor] = (240, 236, 228)
    VERDE_ESCURO: Final[Cor] = (36, 82, 46)
    VERDE: Final[Cor] = (70, 140, 60)
    VERDE_CLARO: Final[Cor] = (118, 186, 72)
    GRAMA_ESCURA: Final[Cor] = (124, 178, 66)
    GRAMA_CLARA: Final[Cor] = (142, 196, 78)
    AMARELO: Final[Cor] = (246, 204, 70)
    LARANJA: Final[Cor] = (226, 128, 48)
    VERMELHO: Final[Cor] = (200, 52, 52)
    MARROM: Final[Cor] = (110, 72, 46)
    AZUL: Final[Cor] = (64, 112, 178)
    AZUL_CLARO: Final[Cor] = (128, 182, 226)
