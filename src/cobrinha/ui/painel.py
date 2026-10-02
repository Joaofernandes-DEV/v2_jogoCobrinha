"""Peças comuns das telas sobrepostas: véu escurecido e textos centralizados."""

from collections.abc import Sequence

import pygame

from cobrinha import recursos
from cobrinha.config import ALTURA_JANELA, LARGURA_JANELA, Cor, Paleta
from cobrinha.ui import texto

Linha = tuple[str, int, Cor]  # (conteúdo, tamanho da fonte, cor)


def criar_veu(opacidade: int) -> pygame.Surface:
    """Camada escura semitransparente do tamanho da janela."""
    veu = pygame.Surface((LARGURA_JANELA, ALTURA_JANELA), pygame.SRCALPHA)
    veu.fill((*Paleta.PRETO, opacidade))
    return veu


def desenhar_linhas(
    superficie: pygame.Surface, linhas: Sequence[Linha], topo: int, espaco: int = 18
) -> int:
    """Desenha as linhas centralizadas a partir de `topo`. Devolve o y logo abaixo da última."""
    y = topo
    for conteudo, tamanho, cor in linhas:
        texto.desenhar_centralizado(superficie, conteudo, tamanho, cor, LARGURA_JANELA // 2, y)
        y += recursos.fonte(tamanho).get_linesize() + espaco
    return y
