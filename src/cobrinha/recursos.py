"""Localização e carregamento único de assets (fontes, imagens e sons).

Os caminhos são resolvidos a partir deste arquivo, então o jogo funciona
independente da pasta de onde é executado (corrige o bug B6 da V1).
Cada asset é carregado do disco uma única vez e reaproveitado (D6).
"""

from functools import cache
from pathlib import Path

import pygame

PASTA_ASSETS = Path(__file__).resolve().parent / "assets"
PASTA_FONTES = PASTA_ASSETS / "fontes"
PASTA_IMAGENS = PASTA_ASSETS / "imagens"
PASTA_SONS = PASTA_ASSETS / "sons"

# VT323 (SIL Open Font License; ver assets/fontes/OFL.txt). Escolhida por ter as
# maiúsculas acentuadas corretas (Í, É, Ê, Ó, Ç...), essenciais num jogo em português.
ARQUIVO_FONTE = PASTA_FONTES / "VT323-Regular.ttf"


def caminho_asset(*partes: str) -> Path:
    """Caminho absoluto para um arquivo dentro de `assets/`."""
    return PASTA_ASSETS.joinpath(*partes)


@cache
def fonte(tamanho: int) -> pygame.font.Font:
    """Fonte do jogo no tamanho pedido, criada uma única vez por tamanho."""
    if ARQUIVO_FONTE.is_file():
        return pygame.font.Font(ARQUIVO_FONTE, tamanho)
    return pygame.font.Font(None, tamanho)


@cache
def imagem(nome: str) -> pygame.Surface:
    """Sprite PNG de `assets/imagens/`, convertido para o formato da tela (exige janela aberta)."""
    return pygame.image.load(PASTA_IMAGENS / f"{nome}.png").convert_alpha()


def limpar_cache() -> None:
    """Descarta fontes e imagens carregadas (necessário ao reiniciar o pygame, ex.: nos testes)."""
    fonte.cache_clear()
    imagem.cache_clear()
