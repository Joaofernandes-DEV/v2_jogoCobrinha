"""Desenho provisório da cobra e da comida com formas simples.

Os sprites em pixel art substituem estas funções na Fase 3.
"""

import pygame

from cobrinha.config import TAMANHO_CELULA, Paleta
from cobrinha.dominio.cobra import Cobra
from cobrinha.dominio.grade import Direcao, Posicao
from cobrinha.ui.campo import celula_para_pixel

MARGEM_SEGMENTO = 2
TAMANHO_OLHO = 4

# Posição dos dois olhos (em pixels dentro da célula) para cada direção da cabeça.
_OLHOS = {
    Direcao.DIREITA: ((15, 6), (15, 15)),
    Direcao.ESQUERDA: ((6, 6), (6, 15)),
    Direcao.CIMA: ((6, 6), (15, 6)),
    Direcao.BAIXO: ((6, 15), (15, 15)),
}


def _retangulo_celula(posicao: Posicao, margem: int = 0) -> pygame.Rect:
    x, y = celula_para_pixel(posicao)
    return pygame.Rect(x, y, TAMANHO_CELULA, TAMANHO_CELULA).inflate(-2 * margem, -2 * margem)


def desenhar_cobra(superficie: pygame.Surface, cobra: Cobra) -> None:
    # Da cauda para a cabeça, para a cabeça ficar sempre por cima.
    for indice in range(len(cobra) - 1, 0, -1):
        cor = Paleta.VERDE if indice % 2 else Paleta.VERDE_CLARO
        superficie.fill(cor, _retangulo_celula(cobra.segmentos[indice], MARGEM_SEGMENTO))

    cabeca = _retangulo_celula(cobra.cabeca, 1)
    superficie.fill(Paleta.VERDE_ESCURO, cabeca)
    for dx, dy in _OLHOS[cobra.direcao]:
        superficie.fill(Paleta.BRANCO, (cabeca.x + dx, cabeca.y + dy, TAMANHO_OLHO, TAMANHO_OLHO))
        superficie.fill(Paleta.PRETO, (cabeca.x + dx + 1, cabeca.y + dy + 1, 2, 2))


def desenhar_comida(superficie: pygame.Surface, posicao: Posicao) -> None:
    fruta = _retangulo_celula(posicao, 4)
    pygame.draw.ellipse(superficie, Paleta.VERMELHO, fruta)
    folha = pygame.Rect(fruta.centerx, fruta.top - 3, 5, 4)
    superficie.fill(Paleta.VERDE, folha)
