"""Localização e carregamento único de assets.

Os caminhos são resolvidos a partir deste arquivo, então o jogo funciona
independente da pasta de onde é executado (corrige o bug B6 da V1).
"""

from functools import cache
from pathlib import Path

import pygame

PASTA_ASSETS = Path(__file__).resolve().parent / "assets"
PASTA_FONTES = PASTA_ASSETS / "fontes"

# Fonte pixel art definida na Fase 3. Até lá, usa-se a fonte padrão do pygame.
ARQUIVO_FONTE = PASTA_FONTES / "fonte_pixel.ttf"


def caminho_asset(*partes: str) -> Path:
    """Caminho absoluto para um arquivo dentro de `assets/`."""
    return PASTA_ASSETS.joinpath(*partes)


@cache
def fonte(tamanho: int) -> pygame.font.Font:
    """Fonte do jogo no tamanho pedido, criada uma única vez por tamanho."""
    if ARQUIVO_FONTE.is_file():
        return pygame.font.Font(ARQUIVO_FONTE, tamanho)
    return pygame.font.Font(None, tamanho)
