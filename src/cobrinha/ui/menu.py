"""Menu vertical navegável pelo teclado. O mouse e o visual final entram na Fase 3 (I1)."""

from collections.abc import Callable
from dataclasses import dataclass

import pygame

from cobrinha import recursos
from cobrinha.config import LARGURA_JANELA, Paleta
from cobrinha.ui import texto

TECLAS_CIMA = (pygame.K_UP, pygame.K_w)
TECLAS_BAIXO = (pygame.K_DOWN, pygame.K_s)
TECLAS_ESQUERDA = (pygame.K_LEFT, pygame.K_a)
TECLAS_DIREITA = (pygame.K_RIGHT, pygame.K_d)
TECLAS_CONFIRMAR = (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)

DISTANCIA_MARCADOR = 18  # px entre o texto e o triângulo de seleção


@dataclass
class ItemMenu:
    rotulo: str | Callable[[], str]  # função para rótulos que mudam (ex.: nível escolhido)
    acao: Callable[[], None] | None = None  # Enter
    ajustar: Callable[[int], None] | None = None  # ← (-1) e → (+1)

    @property
    def texto(self) -> str:
        return self.rotulo() if callable(self.rotulo) else self.rotulo


class Menu:
    def __init__(self, itens: list[ItemMenu]) -> None:
        if not itens:
            raise ValueError("O menu precisa de pelo menos um item.")
        self.itens = itens
        self.selecionado = 0

    @property
    def item_atual(self) -> ItemMenu:
        return self.itens[self.selecionado]

    def tratar_evento(self, evento: pygame.Event) -> bool:
        """Processa a tecla. Devolve True se o menu usou o evento."""
        if evento.type != pygame.KEYDOWN:
            return False
        tecla = evento.key
        item = self.item_atual
        if tecla in TECLAS_CIMA:
            self.selecionado = (self.selecionado - 1) % len(self.itens)
        elif tecla in TECLAS_BAIXO:
            self.selecionado = (self.selecionado + 1) % len(self.itens)
        elif tecla in TECLAS_ESQUERDA and item.ajustar:
            item.ajustar(-1)
        elif tecla in TECLAS_DIREITA and item.ajustar:
            item.ajustar(+1)
        elif tecla in TECLAS_CONFIRMAR and item.acao:
            item.acao()
        else:
            return False
        return True

    def desenhar(
        self, superficie: pygame.Surface, topo: int, tamanho: int = 32, espaco: int = 14
    ) -> None:
        # Passo fixo por linha: a altura da imagem varia com acentos e deixaria o espaçamento torto.
        passo = recursos.fonte(tamanho).get_linesize() + espaco
        for indice, item in enumerate(self.itens):
            selecionado = indice == self.selecionado
            cor = Paleta.AMARELO if selecionado else Paleta.BRANCO
            retangulo = texto.desenhar_centralizado(
                superficie, item.texto, tamanho, cor, LARGURA_JANELA // 2, topo + indice * passo
            )
            if selecionado:
                _desenhar_marcadores(superficie, retangulo)


def _desenhar_marcadores(superficie: pygame.Surface, alvo: pygame.Rect) -> None:
    """Triângulos apontando para o item selecionado, um de cada lado.

    São desenhados, e não texto, para não se confundir com os "<  >" de itens ajustáveis.
    """
    meia_altura = max(alvo.height // 4, 4)
    meio = alvo.centery
    esquerda = alvo.left - DISTANCIA_MARCADOR
    direita = alvo.right + DISTANCIA_MARCADOR
    pontos_esquerda = [
        (esquerda - meia_altura, meio - meia_altura),
        (esquerda, meio),
        (esquerda - meia_altura, meio + meia_altura),
    ]
    pontos_direita = [
        (direita + meia_altura, meio - meia_altura),
        (direita, meio),
        (direita + meia_altura, meio + meia_altura),
    ]
    pygame.draw.polygon(superficie, Paleta.AMARELO, pontos_esquerda)
    pygame.draw.polygon(superficie, Paleta.AMARELO, pontos_direita)
