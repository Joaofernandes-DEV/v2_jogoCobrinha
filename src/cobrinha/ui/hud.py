"""Faixa de HUD no topo da janela (I2): pontos, nível com barra de progresso e recorde."""

from dataclasses import dataclass

import pygame

from cobrinha.config import ALTURA_HUD, LARGURA_JANELA, Cor, Paleta, TamanhoFonte
from cobrinha.ui import texto

MARGEM = 16
ESPESSURA_BORDA = 3
Y_ROTULO = 3
Y_VALOR = 21
LARGURA_BARRA = 180
ALTURA_BARRA = 10


@dataclass(frozen=True)
class DadosHud:
    pontos: int
    recorde: int
    nivel: int
    comidas: int
    meta: int
    mudo: bool = False


def desenhar_hud(superficie: pygame.Surface, dados: DadosHud) -> None:
    superficie.fill(Paleta.CINZA_ESCURO, (0, 0, LARGURA_JANELA, ALTURA_HUD))
    superficie.fill(
        Paleta.PRETO, (0, ALTURA_HUD - ESPESSURA_BORDA, LARGURA_JANELA, ESPESSURA_BORDA)
    )
    _desenhar_contador(superficie, "PONTOS", dados.pontos, Paleta.BRANCO, esquerda=True)
    _desenhar_contador(superficie, "RECORDE", dados.recorde, Paleta.CINZA_CLARO, esquerda=False)
    _desenhar_nivel(superficie, dados)
    if dados.mudo:
        imagem = texto.renderizar("MUDO (M)", TamanhoFonte.MINIMO, Paleta.VERMELHO)
        superficie.blit(imagem, imagem.get_rect(topright=(LARGURA_JANELA - 160, Y_ROTULO)))


def _desenhar_contador(
    superficie: pygame.Surface, rotulo: str, valor: int, cor: Cor, esquerda: bool
) -> None:
    imagem_rotulo = texto.renderizar(rotulo, TamanhoFonte.MINIMO, Paleta.CINZA_CLARO)
    imagem_valor = texto.renderizar(f"{valor:04d}", TamanhoFonte.PEQUENO, cor)
    if esquerda:
        posicoes = {"topleft": (MARGEM, Y_ROTULO)}, {"topleft": (MARGEM, Y_VALOR)}
    else:
        borda = LARGURA_JANELA - MARGEM
        posicoes = {"topright": (borda, Y_ROTULO)}, {"topright": (borda, Y_VALOR)}
    superficie.blit(imagem_rotulo, imagem_rotulo.get_rect(**posicoes[0]))
    superficie.blit(imagem_valor, imagem_valor.get_rect(**posicoes[1]))


def _desenhar_nivel(superficie: pygame.Surface, dados: DadosHud) -> None:
    centro = LARGURA_JANELA // 2
    titulo = texto.renderizar(f"NÍVEL {dados.nivel}", TamanhoFonte.PEQUENO, Paleta.AMARELO)
    superficie.blit(titulo, titulo.get_rect(midtop=(centro, 1)))

    # Barra de progresso da meta de comidas, com contorno preto.
    barra = pygame.Rect(0, 0, LARGURA_BARRA, ALTURA_BARRA)
    barra.midtop = (centro - 24, 30)
    superficie.fill(Paleta.PRETO, barra.inflate(4, 4))
    superficie.fill(Paleta.CINZA, barra)
    proporcao = min(dados.comidas / dados.meta, 1.0) if dados.meta else 0.0
    if proporcao:
        superficie.fill(
            Paleta.VERDE_CLARO, (*barra.topleft, round(barra.width * proporcao), ALTURA_BARRA)
        )

    contagem = texto.renderizar(f"{dados.comidas}/{dados.meta}", TamanhoFonte.MINIMO, Paleta.BRANCO)
    superficie.blit(contagem, contagem.get_rect(midleft=(barra.right + 10, barra.centery)))
