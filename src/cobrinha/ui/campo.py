"""Desenho do campo de jogo e conversão entre células e pixels."""

import pygame

from cobrinha.config import (
    ALTURA_HUD,
    COLUNAS,
    LINHAS,
    TAMANHO_CELULA,
    Paleta,
)
from cobrinha.dominio.grade import GRADE_PADRAO, Posicao


def celula_para_pixel(posicao: Posicao) -> tuple[int, int]:
    """Canto superior esquerdo da célula na janela, já descontando o HUD."""
    return posicao.coluna * TAMANHO_CELULA, ALTURA_HUD + posicao.linha * TAMANHO_CELULA


def criar_fundo_campo() -> pygame.Surface:
    """Xadrez de grama em dois tons, desenhado uma vez e reaproveitado a cada quadro."""
    superficie = pygame.Surface((COLUNAS * TAMANHO_CELULA, LINHAS * TAMANHO_CELULA))
    for posicao in GRADE_PADRAO.todas:
        clara = (posicao.coluna + posicao.linha) % 2 == 0
        cor = Paleta.GRAMA_CLARA if clara else Paleta.GRAMA_ESCURA
        x, y = posicao.coluna * TAMANHO_CELULA, posicao.linha * TAMANHO_CELULA
        superficie.fill(cor, (x, y, TAMANHO_CELULA, TAMANHO_CELULA))
    return superficie
