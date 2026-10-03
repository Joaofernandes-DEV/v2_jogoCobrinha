"""Desenho do campo de jogo e conversão entre células e pixels."""

import math

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


def interpolar_celula(origem: Posicao, destino: Posicao, progresso: float) -> tuple[float, float]:
    """Ponto entre duas células vizinhas, em células (V3): 0 = `origem`, 1 = `destino`.

    Se o salto atravessa a borda (modo sem bordas), o segmento anda 1 célula para fora
    do campo e o resultado volta ao lado oposto, em vez de cruzar o campo inteiro.
    """
    dx = destino.coluna - origem.coluna
    dy = destino.linha - origem.linha
    if abs(dx) > 1:
        dx = -int(math.copysign(1, dx))
    if abs(dy) > 1:
        dy = -int(math.copysign(1, dy))
    coluna = (origem.coluna + dx * progresso) % COLUNAS
    linha = (origem.linha + dy * progresso) % LINHAS
    return coluna, linha


def criar_fundo_campo() -> pygame.Surface:
    """Xadrez de grama em dois tons, desenhado uma vez e reaproveitado a cada quadro."""
    superficie = pygame.Surface((COLUNAS * TAMANHO_CELULA, LINHAS * TAMANHO_CELULA))
    for posicao in GRADE_PADRAO.todas:
        clara = (posicao.coluna + posicao.linha) % 2 == 0
        cor = Paleta.GRAMA_CLARA if clara else Paleta.GRAMA_ESCURA
        x, y = posicao.coluna * TAMANHO_CELULA, posicao.linha * TAMANHO_CELULA
        superficie.fill(cor, (x, y, TAMANHO_CELULA, TAMANHO_CELULA))
    return superficie
