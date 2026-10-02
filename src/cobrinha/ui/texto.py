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
