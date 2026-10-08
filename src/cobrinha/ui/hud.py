"""Faixa de HUD no topo da janela (I2): pontos, nível com barra de progresso e recorde.

Na V3, também mostra os power-ups ativos com os segundos restantes e, no modo contra o
tempo, o relógio no lugar da barra de progresso. O Duelo tem um HUD próprio, com os
pontos de cada jogador na cor da cobra dele.
"""

import math
from dataclasses import dataclass

import pygame

from cobrinha.config import (
    ALTURA_HUD,
    LARGURA_JANELA,
    TEMPO_ALERTA,
    Cor,
    Paleta,
    TamanhoFonte,
)
from cobrinha.ui import texto

MARGEM = 16
ESPESSURA_BORDA = 3
Y_ROTULO = 3
Y_VALOR = 21
LARGURA_BARRA = 180
ALTURA_BARRA = 10
# Duelo: J1 e J3 ficam à esquerda, J2 e J4 à direita; cada par afastado por esta distância.
RECUO_SEGUNDO_JOGADOR = 140


@dataclass(frozen=True)
class DadosHud:
    pontos: int
    recorde: int
    nivel: int
    comidas: int
    meta: int
    modo: str = ""
    mudo: bool = False
    # (rótulo curto, segundos restantes) de cada power-up ativo.
    efeitos: tuple[tuple[str, float], ...] = ()
    # Segundos restantes no modo contra o tempo; None nos outros modos.
    tempo: float | None = None


@dataclass(frozen=True)
class PlacarJogador:
    """Um jogador no HUD do Duelo."""

    nome: str  # ex.: "JOGADOR 1"
    pontos: int
    cor: Cor  # cor de destaque da cobra
    vivo: bool = True


@dataclass(frozen=True)
class DadosHudDuelo:
    jogadores: tuple[PlacarJogador, ...]
    nome_nivel: str
    mudo: bool = False


def desenhar_hud(superficie: pygame.Surface, dados: DadosHud) -> None:
    _desenhar_faixa(superficie)
    _desenhar_contador(superficie, "PONTOS", dados.pontos, Paleta.BRANCO, esquerda=True)
    _desenhar_contador(superficie, "RECORDE", dados.recorde, Paleta.CINZA_CLARO, esquerda=False)
    _desenhar_nivel(superficie, dados)
    if dados.modo:
        modo = texto.renderizar(dados.modo.upper(), TamanhoFonte.MINIMO, Paleta.AZUL_CLARO)
        superficie.blit(modo, modo.get_rect(topleft=(MARGEM + 90, Y_ROTULO)))
    if dados.efeitos:
        resumo = "  ".join(f"{rotulo} {math.ceil(restante)}" for rotulo, restante in dados.efeitos)
        imagem = texto.renderizar(resumo, TamanhoFonte.MINIMO, Paleta.AMARELO)
        superficie.blit(imagem, imagem.get_rect(topleft=(MARGEM + 90, Y_VALOR)))
    if dados.mudo:
        imagem = texto.renderizar("MUDO (M)", TamanhoFonte.MINIMO, Paleta.VERMELHO)
        superficie.blit(imagem, imagem.get_rect(topright=(LARGURA_JANELA - 160, Y_ROTULO)))


def desenhar_hud_duelo(superficie: pygame.Surface, dados: DadosHudDuelo) -> None:
    """Pontos de cada jogador na cor da cobra (cinza e "FORA" se eliminado) e o mapa no meio."""
    _desenhar_faixa(superficie)
    for indice, jogador in enumerate(dados.jogadores):
        valor: int | str = jogador.pontos if jogador.vivo else "FORA"
        cor = jogador.cor if jogador.vivo else Paleta.CINZA
        _desenhar_contador(
            superficie,
            jogador.nome,
            valor,
            cor,
            esquerda=indice % 2 == 0,
            cor_rotulo=cor,
            recuo=(indice // 2) * RECUO_SEGUNDO_JOGADOR,
        )
    centro = LARGURA_JANELA // 2
    titulo = texto.renderizar("DUELO", TamanhoFonte.PEQUENO, Paleta.AMARELO)
    superficie.blit(titulo, titulo.get_rect(midtop=(centro, 1)))
    nivel = texto.renderizar(dados.nome_nivel.upper(), TamanhoFonte.MINIMO, Paleta.AZUL_CLARO)
    superficie.blit(nivel, nivel.get_rect(midtop=(centro, Y_VALOR + 4)))
    if dados.mudo:
        imagem = texto.renderizar("MUDO (M)", TamanhoFonte.MINIMO, Paleta.VERMELHO)
        superficie.blit(imagem, imagem.get_rect(topleft=(centro + 50, Y_ROTULO)))


def _desenhar_faixa(superficie: pygame.Surface) -> None:
    superficie.fill(Paleta.CINZA_ESCURO, (0, 0, LARGURA_JANELA, ALTURA_HUD))
    superficie.fill(
        Paleta.PRETO, (0, ALTURA_HUD - ESPESSURA_BORDA, LARGURA_JANELA, ESPESSURA_BORDA)
    )


def _desenhar_contador(
    superficie: pygame.Surface,
    rotulo: str,
    valor: int | str,
    cor: Cor,
    esquerda: bool,
    cor_rotulo: Cor = Paleta.CINZA_CLARO,
    recuo: int = 0,
) -> None:
    """Rótulo pequeno em cima e valor embaixo, encostados na borda (`recuo` px para dentro)."""
    imagem_rotulo = texto.renderizar(rotulo, TamanhoFonte.MINIMO, cor_rotulo)
    conteudo = f"{valor:04d}" if isinstance(valor, int) else valor
    imagem_valor = texto.renderizar(conteudo, TamanhoFonte.PEQUENO, cor)
    if esquerda:
        x = MARGEM + recuo
        posicoes = {"topleft": (x, Y_ROTULO)}, {"topleft": (x, Y_VALOR)}
    else:
        borda = LARGURA_JANELA - MARGEM - recuo
        posicoes = {"topright": (borda, Y_ROTULO)}, {"topright": (borda, Y_VALOR)}
    superficie.blit(imagem_rotulo, imagem_rotulo.get_rect(**posicoes[0]))
    superficie.blit(imagem_valor, imagem_valor.get_rect(**posicoes[1]))


def _desenhar_nivel(superficie: pygame.Surface, dados: DadosHud) -> None:
    centro = LARGURA_JANELA // 2
    titulo = texto.renderizar(f"NÍVEL {dados.nivel}", TamanhoFonte.PEQUENO, Paleta.AMARELO)
    superficie.blit(titulo, titulo.get_rect(midtop=(centro, 1)))

    if dados.tempo is not None:
        _desenhar_relogio(superficie, dados.tempo)
        return

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


def _desenhar_relogio(superficie: pygame.Surface, tempo: float) -> None:
    """Relógio do modo contra o tempo, no lugar da barra de progresso."""
    cor = Paleta.VERMELHO if tempo <= TEMPO_ALERTA else Paleta.BRANCO
    segundos = math.ceil(tempo)  # 0,2 s restantes ainda mostram 1
    imagem = texto.renderizar(f"TEMPO {segundos:02d}", TamanhoFonte.PEQUENO, cor)
    superficie.blit(imagem, imagem.get_rect(midtop=(LARGURA_JANELA // 2, 25)))
