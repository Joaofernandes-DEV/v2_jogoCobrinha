"""Renderização de texto com cache: cada combinação é desenhada uma única vez."""

from functools import lru_cache

import pygame

from cobrinha import recursos
from cobrinha.config import Cor


@lru_cache(maxsize=256)
def renderizar(texto: str, tamanho: int, cor: Cor) -> pygame.Surface:
    """Superfície com o texto, reaproveitada enquanto o valor não mudar."""
    # antialias=False mantém as bordas nítidas, no estilo pixel art.
    return recursos.fonte(tamanho).render(texto, False, cor)


@lru_cache(maxsize=256)
def _excesso_acima(texto: str, tamanho: int) -> int:
    """Pixels que o texto sobe além da altura normal da fonte.

    Maiúsculas acentuadas (Í, Ó, Ê) passam do topo da fonte, e o pygame aumenta a
    imagem por cima: a linha de base desce e o texto parece fora do alinhamento.
    """
    fonte = recursos.fonte(tamanho)
    metricas = [m for m in fonte.metrics(texto) if m is not None]
    topo_glifos = max((m[3] for m in metricas), default=0)
    return max(0, topo_glifos - fonte.get_ascent())


def desenhar_centralizado(
    superficie: pygame.Surface, texto: str, tamanho: int, cor: Cor, centro_x: int, topo: int
) -> pygame.Rect:
    """Desenha o texto centralizado em `centro_x`, com a linha de base sempre na mesma altura.

    Devolve a caixa da linha (altura padrão da fonte), útil para posicionar marcadores.
    """
    imagem = renderizar(texto, tamanho, cor)
    retangulo = imagem.get_rect(midtop=(centro_x, topo - _excesso_acima(texto, tamanho)))
    superficie.blit(imagem, retangulo)
    altura_linha = recursos.fonte(tamanho).get_height()
    return pygame.Rect(retangulo.left, topo, retangulo.width, altura_linha)


def limpar_cache() -> None:
    renderizar.cache_clear()
    _excesso_acima.cache_clear()
