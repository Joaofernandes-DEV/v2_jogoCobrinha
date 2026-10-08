"""Constantes globais: janela, grade, tempo e paleta de cores.

Toda medida em pixels deriva da grade (ver seção 8.2 do briefing):
32 × 22 células de 25 px + faixa de HUD de 50 px = janela de 800 × 600.
"""

from typing import Final, NamedTuple

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
VOLUME_EFEITOS: Final = 0.9
VOLUME_MUSICA: Final = 0.5

# Jogabilidade
TAMANHO_INICIAL_COBRA: Final = 3
# Comandos de direção guardados à frente do movimento (buffer, J1 do briefing).
LIMITE_FILA_DIRECOES: Final = 2
# Teto de passos recuperados num único quadro, para a cobra não "teleportar"
# depois de um travamento (ex.: arrastar a janela).
MAX_PASSOS_POR_QUADRO: Final = 3

# Fruta dourada (J5): aparece às vezes depois de comer, vale mais e some rápido.
CHANCE_FRUTA_DOURADA: Final = 0.10
DURACAO_FRUTA_DOURADA: Final = 5.0  # segundos de jogo
PONTOS_FRUTA_DOURADA: Final = 5

# Power-ups (V3): aparecem às vezes depois de comer e somem se não forem pegos.
CHANCE_POWER_UP: Final = 0.08
DURACAO_POWER_UP_NO_CAMPO: Final = 7.0  # segundos de jogo
DURACAO_CAMERA_LENTA: Final = 5.0
FATOR_CAMERA_LENTA: Final = 0.5  # multiplica a velocidade da cobra
DURACAO_PONTOS_EM_DOBRO: Final = 8.0
SEGMENTOS_ENCOLHER: Final = 3

# Modo contra o tempo: o relógio corre e comer devolve segundos.
TEMPO_INICIAL: Final = 60.0  # segundos no início da partida
TEMPO_POR_COMIDA: Final = 3.0
TEMPO_POR_FRUTA_DOURADA: Final = 5.0
TEMPO_MAXIMO: Final = 99.0  # o relógio nunca passa disso
TEMPO_ALERTA: Final = 10.0  # abaixo disso o relógio fica vermelho

# Recordes (J6)
TAMANHO_RANKING: Final = 5

# Duelo (V3): de 2 a 4 cobras no mesmo campo; vence quem sobrar por último.
MAXIMO_JOGADORES: Final = 4
COMIDAS_NO_DUELO: Final = 2  # maçãs no campo ao mesmo tempo


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


class PeleCobra(NamedTuple):
    """Cores de uma cobra, todas da paleta. A verde é a original; as outras são do Duelo."""

    nome: str  # mostrado na tela
    sufixo: str  # dos PNGs: cabeca{sufixo}.png, corpo_reto{sufixo}.png...
    escura: Cor  # faixa da borda e escamas
    media: Cor  # corpo
    clara: Cor  # listra do meio
    destaque: Cor  # textos do HUD e luz do controle (legível sobre o HUD escuro)


PELES: Final = (
    PeleCobra(
        "VERDE", "", Paleta.VERDE_ESCURO, Paleta.VERDE, Paleta.VERDE_CLARO, Paleta.VERDE_CLARO
    ),
    PeleCobra(
        "AZUL", "_azul", Paleta.CINZA_ESCURO, Paleta.AZUL, Paleta.AZUL_CLARO, Paleta.AZUL_CLARO
    ),
    PeleCobra("AMARELA", "_amarela", Paleta.LARANJA, Paleta.AMARELO, Paleta.BRANCO, Paleta.AMARELO),
    PeleCobra(
        "VERMELHA", "_vermelha", Paleta.MARROM, Paleta.VERMELHO, Paleta.LARANJA, Paleta.VERMELHO
    ),
)
