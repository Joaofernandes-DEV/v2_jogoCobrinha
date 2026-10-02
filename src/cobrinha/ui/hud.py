"""Faixa de HUD no topo da janela: pontuação, nível (com progresso da meta) e recorde."""

import pygame

from cobrinha.config import ALTURA_HUD, LARGURA_JANELA, Paleta
from cobrinha.ui import texto

TAMANHO_TEXTO = 28
MARGEM = 16
ESPESSURA_BORDA = 3


def desenhar_hud(
    superficie: pygame.Surface,
    pontos: int,
    nivel: int,
    recorde: int,
    comidas: int,
    meta: int,
) -> None:
    faixa = pygame.Rect(0, 0, LARGURA_JANELA, ALTURA_HUD)
    superficie.fill(Paleta.CINZA_ESCURO, faixa)
    superficie.fill(
        Paleta.PRETO,
        (0, ALTURA_HUD - ESPESSURA_BORDA, LARGURA_JANELA, ESPESSURA_BORDA),
    )

    centro_y = (ALTURA_HUD - ESPESSURA_BORDA) // 2
    itens = [
        (f"PONTOS {pontos:03d}", Paleta.BRANCO, "esquerda"),
        (f"NÍVEL {nivel}   {comidas}/{meta}", Paleta.AMARELO, "centro"),
        (f"RECORDE {recorde:03d}", Paleta.CINZA_CLARO, "direita"),
    ]
    for conteudo, cor, alinhamento in itens:
        imagem = texto.renderizar(conteudo, TAMANHO_TEXTO, cor)
        retangulo = imagem.get_rect(centery=centro_y)
        if alinhamento == "esquerda":
            retangulo.left = MARGEM
        elif alinhamento == "centro":
            retangulo.centerx = LARGURA_JANELA // 2
        else:
            retangulo.right = LARGURA_JANELA - MARGEM
        superficie.blit(imagem, retangulo)
